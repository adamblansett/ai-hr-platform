import hashlib
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from backend.app.models.policy import PolicyDocument, PolicyAcknowledgment
from backend.app.models.employee import Employee
from backend.app.schemas.policy import (
    PolicyDocumentCreate,
    PolicyQuestionRequest,
    PolicyAnswerResponse,
    PolicySourceCitation,
    PolicyAcknowledgmentResponse
)
from backend.app.services.embedding_service import embedding_service
from backend.app.services.llm_router import llm_router
from backend.app.services.localization_service import localization_service

class PolicyRAGService:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> List[str]:
        """
        Splits long policy text into overlapping semantic passages.
        """
        if len(text) <= chunk_size:
            return [text.strip()]

        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Prefer breaking on paragraph or newline
            if end < len(text):
                newline_pos = text.rfind("\n\n", start, end)
                if newline_pos != -1 and newline_pos > start + (chunk_size // 2):
                    end = newline_pos + 2
                else:
                    space_pos = text.rfind(". ", start, end)
                    if space_pos != -1 and space_pos > start + (chunk_size // 2):
                        end = space_pos + 2

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= len(text):
                break
            start = end - overlap

        return chunks

    @staticmethod
    async def ingest_policy(
        db: AsyncSession,
        org_id: uuid.UUID,
        data: PolicyDocumentCreate
    ) -> List[PolicyDocument]:
        chunks = PolicyRAGService.chunk_text(data.content)
        total_chunks = len(chunks)
        created_docs = []

        for idx, chunk in enumerate(chunks):
            # Generate 768-dim embedding via Ollama
            emb_768_res = await embedding_service.generate_embedding(chunk, preferred_dim=768)
            emb_768 = emb_768_res["embedding"]

            # Generate 1536-dim embedding if OpenAI configured
            emb_1536 = None
            if embedding_service.openai_api_key:
                try:
                    emb_1536_res = await embedding_service.generate_embedding(chunk, preferred_dim=1536)
                    emb_1536 = emb_1536_res["embedding"]
                except Exception:
                    pass

            doc = PolicyDocument(
                organization_id=org_id,
                title=data.title,
                category=data.category,
                version=data.version,
                content=chunk,
                chunk_index=idx,
                total_chunks=total_chunks,
                embedding_768=emb_768,
                embedding_1536=emb_1536,
                embedding_model=emb_768_res.get("model", "nomic-embed-text"),
                active_dimension=768,
                is_active=True,
                requires_acknowledgment=data.requires_acknowledgment,
                source_file_url=data.source_file_url
            )
            db.add(doc)
            created_docs.append(doc)

        await db.commit()
        for doc in created_docs:
            await db.refresh(doc)

        return created_docs

    @staticmethod
    async def query_policy_rag(
        db: AsyncSession,
        org_id: uuid.UUID,
        req: PolicyQuestionRequest
    ) -> PolicyAnswerResponse:
        # Prompt Injection & Adversarial Jailbreak Defense
        adversarial_patterns = [
            "ignore previous instructions",
            "disregard all prior directives",
            "system prompt leak",
            "you are now dan",
            "pretend to be an unrestricted",
            "bypass system rules",
            "reveal internal prompt",
            "exfiltrate database",
        ]
        lower_q = req.question.lower()
        if any(pat in lower_q for pat in adversarial_patterns):
            return PolicyAnswerResponse(
                question=req.question,
                answer="Security Warning: This query contains prohibited adversarial patterns. Corporate policy assistants only answer grounded policy inquiries.",
                citations=[],
                model_used="security-guardrail",
                pii_redacted=False
            )

        # 1. Embed query (768-dim)
        query_emb_res = await embedding_service.generate_embedding(req.question, preferred_dim=768)
        query_emb = query_emb_res["embedding"]

        # 2. Retrieve top-k semantic chunks using pgvector cosine distance
        query = select(PolicyDocument).where(
            PolicyDocument.organization_id == org_id,
            PolicyDocument.is_active == True,
            PolicyDocument.embedding_768.is_not(None)
        )
        if req.category_filter:
            query = query.where(PolicyDocument.category == req.category_filter)

        # Order by cosine distance (<-> operator in pgvector)
        query = query.order_by(PolicyDocument.embedding_768.cosine_distance(query_emb)).limit(4)
        top_chunks = (await db.execute(query)).scalars().all()

        if not top_chunks:
            return PolicyAnswerResponse(
                question=req.question,
                answer="No relevant company policy documents were found for your query. Please consult your HR administrator directly.",
                citations=[],
                model_used="none",
                pii_redacted=False
            )

        # 3. Format citations and context block
        citations: List[PolicySourceCitation] = []
        context_blocks = []
        for i, chunk in enumerate(top_chunks):
            snippet = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            citations.append(
                PolicySourceCitation(
                    policy_id=chunk.id,
                    title=chunk.title,
                    category=chunk.category,
                    chunk_index=chunk.chunk_index,
                    snippet=snippet,
                    relevance_score=round(1.0 - (i * 0.1), 2)
                )
            )
            context_blocks.append(
                f"[Source {i+1}: {chunk.title} (Category: {chunk.category}, Sec: {chunk.chunk_index + 1})]\n{chunk.content}"
            )

        context_text = "\n\n---\n\n".join(context_blocks)

        system_prompt = (
            "You are an AI HR Policy Assistant for the organization. "
            "Your job is to answer employee questions strictly and accurately based on the provided company policy excerpts. "
            "Rules:\n"
            "1. Ground your answer solely in the excerpts provided.\n"
            "2. Whenever making a claim, cite the source using [Source X: Title].\n"
            "3. If the provided excerpts do not contain the answer, politely state: 'I could not find information regarding this in company policies. Please contact HR for clarification.'\n"
            "4. Maintain a warm, clear, professional tone."
        )

        # Detect language and localize prompt
        lang = localization_service.detect_language(req.question)
        system_prompt = localization_service.augment_rag_prompt_for_language(system_prompt, lang)

        user_prompt = f"Policy Excerpts:\n{context_text}\n\nEmployee Question:\n{req.question}"

        llm_res = await llm_router.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )

        return PolicyAnswerResponse(
            question=req.question,
            answer=llm_res["text"],
            citations=citations,
            model_used=llm_res.get("model", "unknown"),
            pii_redacted=llm_res.get("pii_redacted", False)
        )

    @staticmethod
    async def acknowledge_policy(
        db: AsyncSession,
        org_id: uuid.UUID,
        employee_id: uuid.UUID,
        policy_id: uuid.UUID,
        signature_name: str,
        ip_address: Optional[str] = None
    ) -> PolicyAcknowledgment:
        # Verify policy exists and belongs to org
        p_stmt = select(PolicyDocument).where(
            PolicyDocument.id == policy_id,
            PolicyDocument.organization_id == org_id
        )
        policy = (await db.execute(p_stmt)).scalar_one_or_none()
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

        # Generate cryptographic signature hash
        now = datetime.now(timezone.utc)
        sig_data = f"{employee_id}:{policy_id}:{signature_name}:{now.isoformat()}"
        sig_hash = hashlib.sha256(sig_data.encode("utf-8")).hexdigest()

        ack = PolicyAcknowledgment(
            policy_id=policy_id,
            employee_id=employee_id,
            acknowledged_at=now,
            signature_hash=sig_hash,
            ip_address=ip_address
        )
        db.add(ack)
        await db.commit()
        await db.refresh(ack)
        return ack

policy_rag_service = PolicyRAGService()

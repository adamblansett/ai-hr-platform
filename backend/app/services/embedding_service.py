import httpx
from typing import List, Optional, Dict, Any, Union
from backend.app.core.config import settings

class EmbeddingService:
    """
    Dual-dimension embedding service supporting:
    - 768-dim: Local open-source models (Ollama 'nomic-embed-text', 'bge-base-en-v1.5')
    - 1536-dim: Cloud & extended models (OpenAI 'text-embedding-3-small')
    """

    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.default_ollama_model = settings.EMBEDDING_MODEL # 'nomic-embed-text'
        self.openai_api_key = settings.FALLBACK_OPENAI_API_KEY

    async def generate_embedding(
        self,
        text: str,
        preferred_dim: int = 768,
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates vector embeddings for input text.
        Returns:
            {
                "embedding": List[float],
                "dimension": int (768 or 1536),
                "model": str,
                "provider": str ("ollama" | "openai")
            }
        """
        # Try local Ollama first for 768-dim or if provider is configured as ollama
        if settings.PRIMARY_LLM_PROVIDER == "ollama" or not self.openai_api_key:
            try:
                emb = await self._generate_ollama_embedding(text, model_override or self.default_ollama_model)
                dim = len(emb)
                return {
                    "embedding": emb,
                    "dimension": dim,
                    "model": model_override or self.default_ollama_model,
                    "provider": "ollama"
                }
            except Exception as e:
                if not self.openai_api_key:
                    raise RuntimeError(f"Ollama embedding failed and no OpenAI fallback: {str(e)}")

        # Fallback or cloud target (OpenAI)
        target_dim = preferred_dim if preferred_dim in (768, 1536) else 1536
        emb = await self._generate_openai_embedding(text, dimensions=target_dim)
        return {
            "embedding": emb,
            "dimension": target_dim,
            "model": "text-embedding-3-small",
            "provider": "openai"
        }

    async def _generate_ollama_embedding(self, text: str, model: str) -> List[float]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.ollama_base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("embedding", [])

    async def _generate_openai_embedding(self, text: str, dimensions: int = 1536) -> List[float]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload: Dict[str, Any] = {
                "input": text,
                "model": "text-embedding-3-small",
                "dimensions": dimensions
            }
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]

embedding_service = EmbeddingService()

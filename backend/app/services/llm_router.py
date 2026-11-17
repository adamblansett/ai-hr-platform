import json
import re
import httpx
from typing import Optional, List, Dict, Any, Type, TypeVar
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.services.pii_scrubber import PIIScrubber

T = TypeVar("T", bound=BaseModel)

class LLMRouter:
    """
    Provider-agnostic LLM router supporting local open-weight models via Ollama
    (Llama 3.1 8B, Qwen 2.5 7B, Mistral NeMo 12B) and graceful cloud API fallback,
    enforcing PII scrubbing on all outgoing prompts and structured JSON parsing.
    """

    AVAILABLE_MODELS = {
        "llama3.1": "llama3.1:8b",
        "qwen2.5": "qwen2.5:7b",
        "mistral-nemo": "mistral-nemo:12b",
    }

    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_MODEL
        self.primary_provider = settings.PRIMARY_LLM_PROVIDER

    def sanitize_user_input(self, text: str) -> str:
        """
        Defensive sanitization against prompt injection attacks.
        Neutralizes delimiters and system role hijack attempts.
        """
        sanitized = re.sub(r"(?i)(system\s*:|assistant\s*:|\[INST\]|\[\/INST\]|<\|im_start\|>|<\|im_end\|>)", "[BLOCKED_TOKEN]", text)
        return sanitized

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        sanitize_pii: bool = True
    ) -> Dict[str, Any]:
        target_model = model or self.default_model
        
        # 1. PII Redaction
        processed_prompt = prompt
        pii_was_redacted = False
        if sanitize_pii:
            processed_prompt, pii_was_redacted = PIIScrubber.redact(prompt)

        # 2. Defend against prompt injection
        processed_prompt = self.sanitize_user_input(processed_prompt)

        # 3. Call primary provider (Ollama)
        if self.primary_provider == "ollama":
            try:
                response = await self._call_ollama(processed_prompt, system_prompt, target_model, temperature)
                return {
                    "text": response,
                    "provider": "ollama",
                    "model": target_model,
                    "pii_redacted": pii_was_redacted
                }
            except Exception as e:
                if settings.FALLBACK_OPENAI_API_KEY:
                    return await self._call_openai_fallback(processed_prompt, system_prompt, temperature, pii_was_redacted)
                raise RuntimeError(f"Ollama call failed and no fallback available: {str(e)}")

        # Cloud-first path if configured
        if settings.FALLBACK_OPENAI_API_KEY:
            return await self._call_openai_fallback(processed_prompt, system_prompt, temperature, pii_was_redacted)

        raise ValueError(f"Unsupported or unconfigured LLM provider: {self.primary_provider}")

    async def complete_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.1
    ) -> T:
        """
        Generates completion and parses output directly into a validated Pydantic model.
        """
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        augmented_system = (system_prompt or "") + (
            f"\n\nYou MUST respond STRICTLY with a valid JSON object matching this schema:\n{schema_json}\n"
            "Do NOT include markdown formatting, backticks, or explanatory text before or after the JSON."
        )

        res = await self.complete(
            prompt=prompt,
            system_prompt=augmented_system,
            model=model,
            temperature=temperature
        )
        raw_text = res["text"].strip()
        
        # Clean markdown wrappers if returned
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
            raw_text = re.sub(r"\n?```$", "", raw_text)

        parsed = json.loads(raw_text)
        return schema.model_validate(parsed)

    async def _call_ollama(
        self, prompt: str, system_prompt: Optional[str], model: str, temperature: float
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.ollama_base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": temperature}
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")

    async def _call_openai_fallback(
        self, prompt: str, system_prompt: Optional[str], temperature: float, pii_was_redacted: bool
    ) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.FALLBACK_OPENAI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "temperature": temperature
                }
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return {
                "text": content,
                "provider": "openai_fallback",
                "model": "gpt-4o-mini",
                "pii_redacted": pii_was_redacted
            }

llm_router = LLMRouter()

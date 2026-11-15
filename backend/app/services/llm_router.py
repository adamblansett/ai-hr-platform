import httpx
from typing import Optional, List, Dict, Any
from backend.app.core.config import settings
from backend.app.services.pii_scrubber import PIIScrubber

class LLMRouter:
    """
    Provider-agnostic LLM router supporting local open-weight models via Ollama
    (Llama 3.1 8B, Qwen 2.5 7B, Mistral NeMo 12B) and graceful cloud API fallback,
    enforcing PII scrubbing on all outgoing prompts.
    """

    def __init__(self):
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_MODEL
        self.primary_provider = settings.PRIMARY_LLM_PROVIDER

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

        # 2. Try primary provider (Ollama)
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
                # Fallback to cloud if configured
                if settings.FALLBACK_OPENAI_API_KEY:
                    return await self._call_openai_fallback(processed_prompt, system_prompt, temperature, pii_was_redacted)
                raise RuntimeError(f"Ollama call failed and no fallback available: {str(e)}")

        # Cloud-first path if configured
        if settings.FALLBACK_OPENAI_API_KEY:
            return await self._call_openai_fallback(processed_prompt, system_prompt, temperature, pii_was_redacted)

        raise ValueError(f"Unsupported or unconfigured LLM provider: {self.primary_provider}")

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

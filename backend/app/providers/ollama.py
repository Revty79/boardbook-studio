from __future__ import annotations

import json
import random
import urllib.error
import urllib.request

from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.providers.interfaces import LLMProvider, PromptResult, ProviderError


class OllamaPromptResponse(BaseModel):
    prompt: str
    negative_prompt: str
    seed: int | None = None


class OllamaProvider(LLMProvider):
    """LLM provider backed by Ollama's /api/chat endpoint."""

    name = "ollama"

    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.ollama_model
        self.timeout_seconds = settings.ollama_timeout_seconds
        self.keep_alive = settings.ollama_keep_alive
        self.temperature = settings.ollama_temperature
        self.num_ctx = settings.ollama_num_ctx
        self.default_seed = settings.ollama_seed
        self.api_key = settings.ollama_api_key

        base_url = settings.ollama_base_url.rstrip("/")
        # Accept either ".../api" or the host-only form in env config.
        if base_url.endswith("/api"):
            base_url = base_url[:-4]
        self.base_url = base_url

    def build_initial_prompt(self, payload: dict) -> PromptResult:
        style = payload.get("style", {})
        fallback_negative = str(style.get("negative_prompt_rules", "")).strip()

        messages = [
            {"role": "system", "content": self._system_message()},
            {"role": "user", "content": self._initial_user_message(payload)},
        ]
        structured = self._chat_for_prompt(messages=messages)
        negative_prompt = structured.negative_prompt.strip() or fallback_negative
        return PromptResult(
            prompt=structured.prompt.strip(),
            negative_prompt=negative_prompt,
            seed=structured.seed,
        )

    def refine_prompt(
        self,
        *,
        payload: dict,
        parent_prompt: str,
        parent_negative_prompt: str,
        instruction: str,
    ) -> PromptResult:
        style = payload.get("style", {})
        fallback_negative = (
            str(style.get("negative_prompt_rules", "")).strip()
            or parent_negative_prompt.strip()
        )

        messages = [
            {"role": "system", "content": self._system_message()},
            {
                "role": "user",
                "content": self._refine_user_message(
                    payload=payload,
                    parent_prompt=parent_prompt,
                    parent_negative_prompt=parent_negative_prompt,
                    instruction=instruction,
                ),
            },
        ]
        structured = self._chat_for_prompt(messages=messages)
        negative_prompt = structured.negative_prompt.strip() or fallback_negative
        return PromptResult(
            prompt=structured.prompt.strip(),
            negative_prompt=negative_prompt,
            seed=structured.seed,
        )

    def _system_message(self) -> str:
        return (
            "You are BoardBook Studio's prompt planner for child-friendly board-book art. "
            "Always return strict JSON matching the requested schema. "
            "Keep prompts clear, visual, and consistent with provided locked traits."
        )

    def _initial_user_message(self, payload: dict) -> str:
        characters = payload.get("characters", [])
        style = payload.get("style", {})
        page_text = str(payload.get("page_text", "")).strip()

        character_lines: list[str] = []
        for char in characters:
            traits = ", ".join(char.get("locked_traits", [])) or "none"
            refs = ", ".join(char.get("reference_images", [])) or "none"
            character_lines.append(
                f"- Name: {char.get('name', 'Character')}\n"
                f"  Description: {char.get('description', '')}\n"
                f"  Personality: {char.get('personality', '')}\n"
                f"  Locked traits: {traits}\n"
                f"  References: {refs}"
            )

        return (
            "Build an image-generation prompt for a children's board-book illustration.\n"
            "Return JSON only with fields: prompt, negative_prompt, seed.\n\n"
            f"Story page text:\n{page_text}\n\n"
            "Characters:\n"
            + ("\n".join(character_lines) if character_lines else "- none")
            + "\n\n"
            "Style profile:\n"
            f"- Visual style: {style.get('visual_style', '')}\n"
            f"- Color palette: {style.get('color_palette', '')}\n"
            f"- Lighting: {style.get('lighting', '')}\n"
            f"- Composition: {style.get('composition', '')}\n"
            f"- Negative rules: {style.get('negative_prompt_rules', '')}\n\n"
            "Guidelines:\n"
            "- Keep character identity and locked traits stable.\n"
            "- Keep scene child-safe and warm.\n"
            "- Negative prompt should be concise and practical.\n"
            "- Seed may be null or integer."
        )

    def _refine_user_message(
        self,
        *,
        payload: dict,
        parent_prompt: str,
        parent_negative_prompt: str,
        instruction: str,
    ) -> str:
        style = payload.get("style", {})
        page_text = str(payload.get("page_text", "")).strip()
        characters = payload.get("characters", [])

        trait_lines: list[str] = []
        for char in characters:
            traits = ", ".join(char.get("locked_traits", [])) or "none"
            trait_lines.append(f"- {char.get('name', 'Character')}: {traits}")

        return (
            "Refine an existing board-book image prompt.\n"
            "Return JSON only with fields: prompt, negative_prompt, seed.\n\n"
            f"Current prompt:\n{parent_prompt}\n\n"
            f"Current negative prompt:\n{parent_negative_prompt}\n\n"
            f"Refinement request:\n{instruction.strip()}\n\n"
            f"Story page text:\n{page_text}\n\n"
            "Locked character traits:\n"
            + ("\n".join(trait_lines) if trait_lines else "- none")
            + "\n\n"
            "Style profile:\n"
            f"- Visual style: {style.get('visual_style', '')}\n"
            f"- Color palette: {style.get('color_palette', '')}\n"
            f"- Lighting: {style.get('lighting', '')}\n"
            f"- Composition: {style.get('composition', '')}\n"
            f"- Negative rules: {style.get('negative_prompt_rules', '')}\n\n"
            "Guidelines:\n"
            "- Apply only the requested change unless otherwise needed.\n"
            "- Preserve core character identity and locked traits.\n"
            "- Keep output child-friendly and stylistically consistent.\n"
            "- Seed may be null or integer."
        )

    def _chat_for_prompt(self, *, messages: list[dict[str, str]]) -> OllamaPromptResponse:
        schema = OllamaPromptResponse.model_json_schema()
        options: dict[str, int | float] = {
            "temperature": self.temperature,
            "num_ctx": self.num_ctx,
        }
        seed_to_use = self.default_seed
        if seed_to_use is not None:
            options["seed"] = seed_to_use

        payload = {
            "model": self.model,
            "messages": messages,
            "format": schema,
            "stream": False,
            "options": options,
            "keep_alive": self.keep_alive,
        }
        response_json = self._post_json("/api/chat", payload)
        message = response_json.get("message", {})
        content = message.get("content")
        if not isinstance(content, str):
            raise ProviderError("Ollama response did not include message.content text.")

        parsed = self._parse_structured_content(content)
        if parsed.seed is None:
            parsed.seed = seed_to_use if seed_to_use is not None else random.randint(1, 999999)
        if not parsed.prompt.strip():
            raise ProviderError("Ollama returned an empty prompt.")
        return parsed

    def _parse_structured_content(self, content: str) -> OllamaPromptResponse:
        text = content.strip()
        try:
            return OllamaPromptResponse.model_validate_json(text)
        except ValidationError:
            pass

        # Some models wrap JSON in markdown fences or extra prose.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                return OllamaPromptResponse.model_validate_json(candidate)
            except ValidationError as exc:
                raise ProviderError(
                    "Ollama returned JSON that did not match the expected prompt schema."
                ) from exc

        raise ProviderError("Ollama did not return parseable JSON for prompt output.")

    def _post_json(self, path: str, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        request = urllib.request.Request(url=url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise ProviderError("Ollama returned a non-object JSON response.")
                return data
        except urllib.error.HTTPError as exc:
            error_text = ""
            try:
                payload_text = exc.read().decode("utf-8")
                payload_json = json.loads(payload_text)
                if isinstance(payload_json, dict):
                    error_text = str(payload_json.get("error", ""))
            except Exception:
                error_text = ""

            detail = error_text or f"HTTP {exc.code} from Ollama."
            raise ProviderError(f"Ollama request failed: {detail}") from exc
        except urllib.error.URLError as exc:
            raise ProviderError(
                "Unable to reach Ollama. Check OLLAMA_BASE_URL and confirm Ollama is running."
            ) from exc
        except TimeoutError as exc:
            raise ProviderError("Ollama request timed out.") from exc

from app.providers.interfaces import LLMProvider, PromptResult


class OllamaProvider(LLMProvider):
    """Placeholder provider for future local Ollama integration."""

    name = "ollama"

    def build_initial_prompt(self, payload: dict) -> PromptResult:
        raise NotImplementedError("OllamaProvider is a placeholder in MVP. Use MockLLMProvider for now.")

    def refine_prompt(
        self,
        *,
        payload: dict,
        parent_prompt: str,
        parent_negative_prompt: str,
        instruction: str,
    ) -> PromptResult:
        raise NotImplementedError("OllamaProvider is a placeholder in MVP. Use MockLLMProvider for now.")

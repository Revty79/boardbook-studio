from app.providers.interfaces import GeneratedImageResult, ImageGenerationProvider


class ComfyUIProvider(ImageGenerationProvider):
    """Placeholder provider for future ComfyUI integration."""

    name = "comfyui"

    def generate_image(self, *, prompt: str, negative_prompt: str, seed: int | None) -> GeneratedImageResult:
        raise NotImplementedError("ComfyUIProvider is a placeholder in MVP. Use MockImageProvider for now.")

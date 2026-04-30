from __future__ import annotations

from datetime import datetime
from pathlib import Path
from random import randint

from PIL import Image, ImageDraw

from app.core.config import get_settings
from app.providers.interfaces import GeneratedImageResult, ImageGenerationProvider


class MockImageProvider(ImageGenerationProvider):
    name = "mock-image"

    def __init__(self) -> None:
        settings = get_settings()
        self.media_root = Path(settings.media_dir)
        self.generated_dir = self.media_root / "generated"
        self.generated_dir.mkdir(parents=True, exist_ok=True)

    def generate_image(self, *, prompt: str, negative_prompt: str, seed: int | None) -> GeneratedImageResult:
        actual_seed = seed if seed is not None else randint(1, 999999)
        now = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        filename = f"mock_{now}_{actual_seed}.png"
        file_path = self.generated_dir / filename

        image = Image.new("RGB", (1024, 1024), color=(243, 236, 221))
        draw = ImageDraw.Draw(image)

        draw.rectangle([(60, 60), (964, 964)], outline=(173, 149, 124), width=6)
        draw.text((90, 90), "BoardBook Studio Mock Generation", fill=(77, 61, 44))
        draw.text((90, 130), f"Seed: {actual_seed}", fill=(77, 61, 44))

        snippet = (prompt or "").strip()[:420]
        if snippet:
            draw.multiline_text((90, 190), snippet, fill=(62, 50, 36), spacing=6)

        image.save(file_path)

        relative_path = f"generated/{filename}"
        return GeneratedImageResult(image_path=relative_path, provider=self.name, seed=actual_seed)

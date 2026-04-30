from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Character, Generation, Project, StoryPage, StyleProfile
from app.providers.mock_image import MockImageProvider


def seed_demo_data(db: Session) -> None:
    existing = db.scalar(select(Project.id).limit(1))
    if existing is not None:
        return

    project = Project(
        title="Moonlight Pajamas",
        description="A cozy bedtime board-book demo project.",
    )
    db.add(project)
    db.flush()

    character = Character(
        project_id=project.id,
        name="Mila",
        description="A curious toddler with round cheeks and a tiny braid.",
        personality="Gentle, sleepy, playful",
        locked_traits=["round cheeks", "tiny braid", "soft button nose"],
    )
    db.add(character)
    db.flush()

    style = StyleProfile(
        project_id=project.id,
        visual_style="Soft watercolor with simple shapes",
        color_palette="Peach, sky blue, cream",
        lighting="Warm bedside lamp glow",
        composition="Character in foreground with minimal bedroom details",
        negative_prompt_rules="No photorealism. No harsh shadows. No scary features.",
    )
    db.add(style)
    db.flush()

    page = StoryPage(
        project_id=project.id,
        title="Page 1",
        page_number=1,
        text_content=(
            "Mila yawned and hugged her bunny tight while the moon peeked through the curtains."
        ),
    )
    db.add(page)
    db.flush()

    # Ensure media directory exists before generating demo output.
    settings = get_settings()
    Path(settings.media_dir).mkdir(parents=True, exist_ok=True)

    image_provider = MockImageProvider()
    generated = image_provider.generate_image(
        prompt=(
            "Children's board-book illustration of Mila in striped pajamas hugging a bunny in a cozy bedroom."
        ),
        negative_prompt="No photorealism. No scary elements.",
        seed=4242,
    )

    generation = Generation(
        page_id=page.id,
        prompt="Cozy bedtime scene with Mila hugging bunny.",
        negative_prompt="No photorealism. No scary elements.",
        seed=generated.seed,
        provider=generated.provider,
        image_path=generated.image_path,
        generation_type="mock",
    )
    db.add(generation)
    db.flush()

    page.approved_generation_id = generation.id
    db.commit()

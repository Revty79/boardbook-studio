from app.models import Character, StoryPage, StyleProfile


def build_prompt_payload(*, page: StoryPage, characters: list[Character], style_profile: StyleProfile | None) -> dict:
    style_data = {
        "visual_style": style_profile.visual_style if style_profile else "Soft storybook watercolor",
        "color_palette": style_profile.color_palette if style_profile else "Warm pastels",
        "lighting": style_profile.lighting if style_profile else "Gentle diffuse light",
        "composition": style_profile.composition if style_profile else "Centered character with simple background",
        "negative_prompt_rules": (
            style_profile.negative_prompt_rules
            if style_profile
            else "No photorealism. No horror. No unsettling proportions."
        ),
    }

    character_data = [
        {
            "id": char.id,
            "name": char.name,
            "description": char.description or "",
            "personality": char.personality or "",
            "locked_traits": char.locked_traits or [],
            "reference_images": [ref.image_path for ref in char.references],
        }
        for char in characters
    ]

    return {
        "page_id": page.id,
        "page_text": page.text_content,
        "style": style_data,
        "characters": character_data,
    }

from __future__ import annotations

import random

from app.providers.interfaces import LLMProvider, PromptResult


class MockLLMProvider(LLMProvider):
    name = "mock-llm"

    def build_initial_prompt(self, payload: dict) -> PromptResult:
        page_text = payload.get("page_text", "")
        style = payload.get("style", {})
        characters = payload.get("characters", [])

        character_lines = []
        for char in characters:
            traits = ", ".join(char.get("locked_traits", [])) or "consistent child-book proportions"
            character_lines.append(
                f"{char.get('name', 'Character')}: {char.get('description', 'No description')} | locked traits: {traits}"
            )

        style_line = (
            f"Style: {style.get('visual_style', 'storybook watercolor')}; "
            f"Palette: {style.get('color_palette', 'warm pastels')}; "
            f"Lighting: {style.get('lighting', 'soft ambient')}; "
            f"Composition: {style.get('composition', 'clear silhouette with simple background')}"
        )

        prompt = (
            "Children's board-book illustration. "
            + style_line
            + " Characters: "
            + " || ".join(character_lines)
            + f" Scene text: {page_text.strip()}"
        )
        negative = style.get(
            "negative_prompt_rules",
            "No photorealism, no horror, no unsettling anatomy, no text overlays.",
        )

        return PromptResult(prompt=prompt, negative_prompt=negative, seed=random.randint(1, 999999))

    def refine_prompt(
        self,
        *,
        payload: dict,
        parent_prompt: str,
        parent_negative_prompt: str,
        instruction: str,
    ) -> PromptResult:
        refinement = (
            f"{parent_prompt} Refinement instruction: {instruction}. "
            "Preserve previously locked character traits and visual identity."
        )
        negative = payload.get("style", {}).get("negative_prompt_rules", parent_negative_prompt)
        return PromptResult(prompt=refinement, negative_prompt=negative, seed=random.randint(1, 999999))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import StyleProfile


class StyleProfileRepository:
    def get_for_project(self, db: Session, project_id: int) -> StyleProfile | None:
        stmt = select(StyleProfile).where(StyleProfile.project_id == project_id)
        return db.scalar(stmt)

    def upsert(
        self,
        db: Session,
        *,
        project_id: int,
        visual_style: str,
        color_palette: str,
        lighting: str,
        composition: str,
        negative_prompt_rules: str,
    ) -> StyleProfile:
        profile = self.get_for_project(db, project_id)
        if profile is None:
            profile = StyleProfile(
                project_id=project_id,
                visual_style=visual_style,
                color_palette=color_palette,
                lighting=lighting,
                composition=composition,
                negative_prompt_rules=negative_prompt_rules,
            )
            db.add(profile)
        else:
            profile.visual_style = visual_style
            profile.color_palette = color_palette
            profile.lighting = lighting
            profile.composition = composition
            profile.negative_prompt_rules = negative_prompt_rules
        db.commit()
        db.refresh(profile)
        return profile

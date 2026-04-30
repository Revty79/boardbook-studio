from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    characters: Mapped[list[Character]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Character.id"
    )
    style_profile: Mapped[StyleProfile | None] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=False
    )
    story_pages: Mapped[list[StoryPage]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="StoryPage.page_number"
    )


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    personality: Mapped[str | None] = mapped_column(Text, nullable=True)
    locked_traits: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project] = relationship(back_populates="characters")
    references: Mapped[list[CharacterReference]] = relationship(
        back_populates="character", cascade="all, delete-orphan", order_by="CharacterReference.id"
    )


class CharacterReference(Base):
    __tablename__ = "character_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    character: Mapped[Character] = relationship(back_populates="references")


class StyleProfile(Base):
    __tablename__ = "style_profiles"
    __table_args__ = (UniqueConstraint("project_id", name="uq_style_profile_project"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    visual_style: Mapped[str] = mapped_column(String(200), default="Soft storybook watercolor")
    color_palette: Mapped[str] = mapped_column(String(200), default="Warm pastels")
    lighting: Mapped[str] = mapped_column(String(200), default="Gentle morning light")
    composition: Mapped[str] = mapped_column(String(300), default="Simple foreground character with cozy background")
    negative_prompt_rules: Mapped[str] = mapped_column(
        Text,
        default="No scary elements. No photorealism. Keep child-friendly shapes.",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project] = relationship(back_populates="style_profile")


class StoryPage(Base):
    __tablename__ = "story_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), default="Untitled Page")
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    text_content: Mapped[str] = mapped_column(Text, default="")
    approved_generation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project] = relationship(back_populates="story_pages")
    generations: Mapped[list[Generation]] = relationship(
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="Generation.created_at",
        foreign_keys="Generation.page_id",
    )


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("story_pages.id", ondelete="CASCADE"), index=True)
    parent_generation_id: Mapped[int | None] = mapped_column(ForeignKey("generations.id"), nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str] = mapped_column(Text, default="")
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provider: Mapped[str] = mapped_column(String(80), default="mock-image")
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    generation_type: Mapped[str] = mapped_column(String(30), default="mock")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    page: Mapped[StoryPage] = relationship(back_populates="generations", foreign_keys=[page_id])
    parent_generation: Mapped[Generation | None] = relationship(
        remote_side=[id], back_populates="child_generations", foreign_keys=[parent_generation_id]
    )
    child_generations: Mapped[list[Generation]] = relationship(back_populates="parent_generation")
    refinement_messages: Mapped[list[RefinementMessage]] = relationship(
        back_populates="generation", cascade="all, delete-orphan", order_by="RefinementMessage.created_at"
    )


class RefinementMessage(Base):
    __tablename__ = "refinement_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    generation_id: Mapped[int] = mapped_column(
        ForeignKey("generations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), default="user")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    generation: Mapped[Generation] = relationship(back_populates="refinement_messages")

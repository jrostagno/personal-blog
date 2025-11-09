from typing import Annotated, List, Literal, Optional

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Tag(BaseModel):
    name: str = Field(
        ..., min_length=2, max_length=30, description="Nombre de la etiqueta"
    )
    model_config = ConfigDict(from_attributes=True)


class Author(BaseModel):
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)
    author: Optional[Author] = None
    image_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Titulo del post",
        examples=["Este es el titulo del post"],
    )

    content: Optional[str] = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post minimo 10 caracteres",
        examples=["Este es un contenido sobre programacion"],
    )

    tags: List[Tag] = Field(default_factory=list)  # []

    # author:Optional[Author]=None

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "span" in value.lower():
            raise ValueError("El titulo no debe contener span")
        return value

    @classmethod
    def as_form(
        cls,
        title: Annotated[str, Form(min_length=3)],
        content: Annotated[str, Form(min_length=10)],
        tags: Annotated[List[str], Form()] = None,
    ):
        tag_objs = [Tag(name=t) for t in (tags or [])]
        return cls(title=title, content=content, tags=tag_objs)


class PostPublic(PostBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str
    model_config = ConfigDict(from_attributes=True)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None


class PaginatedPost(BaseModel):
    page: int
    total: int
    total_pages: int
    per_page: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[PostPublic]



from __future__ import annotations
from typing import List, Optional,TYPE_CHECKING
from sqlalchemy import  Column,Table,DateTime, ForeignKey, Integer, String,Text , func, null
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

if TYPE_CHECKING:
    from .author import AuthorORM
    from .tag import TagORM



post_tags=Table("post_tags",
                Base.metadata,
                Column('post_id',ForeignKey("posts.id", ondelete="CASCADE"),primary_key=True), 
                Column('tag_id',ForeignKey("tags.id",ondelete="CASCADE"),primary_key=True)
                )
    
class PostORM(Base):
    __tablename__ = "posts"
    id:Mapped[int]=mapped_column(Integer, primary_key=True)
    title:Mapped[str]=mapped_column(String(150),nullable=False)
    content:Mapped[str]=mapped_column(Text, nullable=False)
    image_url:Mapped[Optional[str]]=mapped_column(String(300), nullable=True)
    created_at:Mapped[DateTime]=mapped_column(DateTime ,server_default=func.now(),nullable=False)
    
    author_id:Mapped[Optional[int]]=mapped_column(ForeignKey('authors.id'))
    author:Mapped[Optional[AuthorORM]]=relationship(back_populates='posts')
    
    tags:Mapped[List["TagORM"]]=relationship(secondary=post_tags,back_populates='posts',lazy='selectin',passive_deletes=True)
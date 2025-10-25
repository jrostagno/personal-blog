

from typing import List, Optional
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base, engine

# TABLA INTERMEDIA RELACION n:m

post_tags=Table("post_tags",
                Base.metadata,
                Column('post_id',ForeignKey("posts.id", ondelete="CASCADE"),primary_key=True), 
                Column('tag_id',ForeignKey("tags.id",ondelete="CASCADE"),primary_key=True)
                )
    

class AuthorORM(Base):
    __tablename__="authors"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(100),nullable=False)
    email:Mapped[str]= mapped_column(String(100), unique=True, index=True)
    
    posts:Mapped[List["PostORM"]]=relationship(back_populates="author")   # UN Author puede tener muchos Post
    
    


class PostORM(Base):
    __tablename__ = "posts"
    id:Mapped[int]=mapped_column(Integer, primary_key=True)
    title:Mapped[str]=mapped_column(String(150),nullable=False)
    content:Mapped[str]=mapped_column(Text, nullable=False)
    created_at:Mapped[DateTime]=mapped_column(DateTime ,server_default=func.now(),nullable=False)
    
    author_id:Mapped[Optional[int]]=mapped_column(ForeignKey('authors.id'))
    author:Mapped[Optional[AuthorORM]]=relationship(back_populates='posts')
    
    tags:Mapped[List["TagORM"]]=relationship(secondary=post_tags,back_populates='posts',lazy='selectin',passive_deletes=True)



class TagORM(Base):
    __tablename__='tags'
    id:Mapped[int]=mapped_column(Integer,primary_key=True, index=True)
    name:Mapped[str]=mapped_column(String(100),unique=True,index=True)
    
    posts:Mapped[List["PostORM"]]= relationship(secondary=post_tags,back_populates='tags', lazy='selectin', passive_deletes=True)
    
    



    
    

    

    
    
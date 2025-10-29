from math import ceil
from typing import List, Literal, Optional, Union
from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from pydantic_core.core_schema import tagged_union_schema
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, selectinload



# 👇 ¡IMPORTAR modelos antes de create_all!
from app.core.db import Base,engine,get_db
from app.models.models import AuthorORM, PostORM, TagORM, post_tags
from app.api.posts.schemas import PaginatedPost, PostCreate, PostPublic, PostSummary  

# Solo en desarrollo: crear tablas si no existen
Base.metadata.create_all(bind=engine)

app=FastAPI(title='Personal Blog')




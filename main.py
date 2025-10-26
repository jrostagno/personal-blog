from math import ceil
from typing import List, Literal, Optional
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.db import Base, engine, get_db


# 👇 ¡IMPORTAR modelos antes de create_all!
from app.models.models import AuthorORM, PostORM, TagORM, post_tags
from app.schemas.schemas import PaginatedPost, PostCreate, PostPublic  

# Solo en desarrollo: crear tablas si no existen
Base.metadata.create_all(bind=engine)

app=FastAPI(title='Personal Blog')

@app.get("/posts",response_model=PaginatedPost)
def list_post(
    text: Optional[str] = Query(default=None, deprecated=True,description="parametro obsoleto usa query en su lugar"),
    query:Optional[str]=Query(default=None,description="Busca por titulo de post", alias='Search',min_length=3,max_length=50, pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$"),
    per_page:int=Query(10,ge=1,le=50, description="Numero de resultados(1-50)"),
    page:int=Query(1,ge=1,description="Numero de pagina >=1"),
    order_by:Literal['id','title']=Query("id",description="campo de orden"),
    direction:Literal['asc','desc']=Query('asc',description='Direccion de orden'),
    db:Session=Depends(get_db)    
):
    
 results=select(PostORM)
 
 query= query or text
 
 if query:
     results=results.where(PostORM.title.ilike(f"%{query}%"))

 total=db.scalar(select(func.count()).select_from(results.subquery())) or 0
 total_pages= ceil(total/per_page) if total>0 else 0
 current_page= 1 if total_pages==0 else min(page,total_pages)
 if order_by=='id':
     order_col= PostORM.id
 else:
     order_col= func.lower(PostORM.title)
     
 results = results.order_by(
        order_col.asc() if direction == "asc" else order_col.desc())
     # results = sorted(
    #     results, key=lambda post: post[order_by], reverse=(direction == "desc"))
 if total_pages == 0:
    items: List[PostPublic] = []
 else:
    start = (current_page - 1) * per_page
    posts_orm = db.execute(results.limit(
            per_page).offset(start)).scalars().all()
    items = [PostPublic.model_validate(post) for post in posts_orm]   #convertir tus modelos de SQLAlchemy en modelos de respuesta Pydantic.
    
    # model_validate() toma los atributos del objeto ORM y genera una instancia validada de PostPublic

 has_prev = current_page > 1
 has_next = current_page < total_pages if total_pages > 0 else False

 return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items
    )




# @app.post("/post/")
# def home():

@app.post("/posts", response_model=PostPublic,response_description="Post Creado con exito",status_code=status.HTTP_201_CREATED)
def create_post(post:PostCreate,db:Session=Depends(get_db)):
    author_obj=None
    
    if post.author:
        author_obj= db.execute(select(AuthorORM).where(AuthorORM.email == post.author.email)).scalar_one_or_none()
        
        if not author_obj:
            author_obj=AuthorORM(name=post.author.name,email=post.author.email)
            db.add(author_obj)
            db.flush()
    
    new_post=PostORM(title=post.title,content=post.content, author=author_obj)
    
    for tag in post.tags:
        tag_obj=db.execute(select(TagORM).where(TagORM.name==tag.name)).scalar_one_or_none()
        if not tag_obj:
            tag_obj= TagORM(name=tag.name)
            db.add(tag_obj)
            db.flush()
        new_post.tags.append(tag_obj)
        
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return PostPublic.model_validate(new_post)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail='El titulo ya existe, prueba con otro')
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500,detail="Error al crear el post")
    
    

@app.delete("/delete/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id:int,db:Session=Depends(get_db)):
    post_to_delete= db.execute(select(PostORM).where(PostORM.id==post_id)).scalar_one_or_none()
    
    if not post_to_delete:
        raise HTTPException(status_code=404,detail='Post no encontrado')
    
    db.delete(post_to_delete)
    db.commit()
    
    return
    

        
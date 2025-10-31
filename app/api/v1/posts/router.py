from math import ceil
from typing import Literal, Optional, Union,List
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, selectinload
from app.core.db import get_db
from app.core.security import get_current_user, oauth2_scheme
from app.models.author import AuthorORM
from app.models.post import PostORM
from app.models.tag import TagORM
from .schemas import (PostPublic,PaginatedPost,PostCreate,PostSummary,PostBase, PostUpdate)

from .repository import PostRepository


router = APIRouter(prefix="/posts",tags=["posts"])



@router.get("/by-tags", response_model=List[PostPublic])
def get_post_by_tags(
    tags: List[str] = Query(
        ...,
        description="Una o más etiquetas. Ejemplo: ?tags=python&tags=java",
    ),
    db: Session = Depends(get_db),
):
    repository = PostRepository(db)
    posts = repository.by_tags(tags)
    return [PostPublic.model_validate(p, from_attributes=True) for p in posts]



@router.put("/{post_id}",response_model=PostPublic,response_description="Post actualizado con exito",status_code=status.HTTP_200_OK)
def update_post(post_id:int, post:PostUpdate,db:Session=Depends(get_db),user=Depends(get_current_user)):
    
    repository= PostRepository(db)
    post_to_update =repository.get(post_id)
    
    if not post_to_update:
         raise HTTPException(status_code=404, detail="Post no encontrado")
    try:
     updates= post.model_dump(exclude_unset=True)
     new_post= repository.update_post(post_to_update,updates)
     db.commit()
     db.refresh(new_post)
     return new_post
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail='El titulo ya existe, prueba con otro')
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500,detail="Error al actualizar el post")
        
    

@router.delete("/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    
    repository= PostRepository(db)
    post_to_delete =repository.get(post_id)
    if not post_to_delete:
         raise HTTPException(status_code=404, detail="Post no encontrado")
     
    try:    
     repository.delete_post(post_to_delete)   
     db.commit()
    except SQLAlchemyError:
     db.rollback()
     raise HTTPException(status_code=500,detail="Error al eliminar el post")
    
    




@router.get("/{post_id}",response_model=Union[PostPublic,PostSummary], response_description="Post encontrado")
def get_post_by_id(
    post_id:int=Path(...,ge=1,title="Id del post",description="Identificador del post",example="ejemplo 1"),
    include_content:bool= Query(default=True,description="Incluir o no el Contenido"),
    db:Session=Depends(get_db)
    ):
    
    repository= PostRepository(db)
    post_fin=repository.get(post_id)
    
    if not post_fin:
        raise HTTPException(status_code=404,detail="Post no encontrado")
    if include_content:
        return PostPublic.model_validate(post_fin,from_attributes=True)
    
    return PostSummary.model_validate(post_fin,from_attributes=True)


@router.post("", response_model=PostPublic,response_description="Post Creado con exito",status_code=status.HTTP_201_CREATED)
def create_post(post:PostCreate,db:Session=Depends(get_db), user=Depends(get_current_user)):
    
    repository= PostRepository(db)        
    try:
        
        new_post = repository.create_post(
            title=post.title,
            content=post.content,
            author=user,
            tags=[tag.model_dump() for tag in post.tags]
        )
       
        db.commit()
        db.refresh(new_post)
        return PostPublic.model_validate(new_post)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409,detail='El titulo ya existe, prueba con otro')
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500,detail="Error al crear el post")
    
    
    
    
@router.get("",response_model=PaginatedPost)
def list_post(
            text: Optional[str] = Query(default=None, deprecated=True,description="parametro obsoleto usa query en su lugar"),
            query:Optional[str]=Query(default=None,description="Busca por titulo de post", alias='Search',min_length=3,max_length=50, pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜ-]+$"),
            per_page:int=Query(10,ge=1,le=50, description="Numero de resultados(1-50)"),
            page:int=Query(1,ge=1,description="Numero de pagina >=1"),
            order_by:Literal['id','title']=Query("id",description="campo de orden"),
            direction:Literal['asc','desc']=Query('asc',description='Direccion de orden'),
            db:Session=Depends(get_db)    
        ):
    repository= PostRepository(db)
    query= query or text
    
    total,items= repository.search(query,order_by,direction,page,per_page)
    
    total_pages= ceil(total/per_page) if total>0 else 0 
    
    current_page= 1 if total_pages==0 else min(page,total_pages)
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
    

@router.get("/secure")
def secure_endpoint(token:str=Depends(oauth2_scheme)):
    return {"message":"Acceso con Token", "token_recibido":token}

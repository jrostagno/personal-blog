
from math import ceil
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select,func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.v1.posts.schemas import PostPublic
from app.models.author import AuthorORM
from app.models.post import PostORM
from app.models.tag import TagORM


# ESTA CLASE DE  ENCARGA DE LAS CONSULTAS

class PostRepository:
    def __init__(self,db:Session):
        self.db=db
        
    def get(self,post_id:int)->Optional[PostORM]:
        post_find= select(PostORM).where(PostORM.id==post_id)
        return self.db.execute(post_find).scalar_one_or_none()
    
    
    def search(
        self,
        query:Optional[str],
        order_by:str,
        direction:str,
        page:int,
        per_page:int
        )->Tuple[int,List[PostORM]]:
        
        
        results=select(PostORM)
     
        if query:
            results=results.where(PostORM.title.ilike(f"%{query}%"))

        total=self.db.scalar(select(func.count()).select_from(results.subquery())) or 0
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
            posts_orm = self.db.execute(results.limit(
                    per_page).offset(start)).scalars().all()
            items = [PostPublic.model_validate(post) for post in posts_orm]   #convertir tus modelos de SQLAlchemy en modelos de respuesta Pydantic.
            
            # model_validate() toma los atributos del objeto ORM y genera una instancia validada de PostPublic
        return total,items
    
    def by_tags(self,tags:List[str])->List[PostORM]:
            normalized_tags_names=[tag.strip().lower() for tag in tags if tag.strip()]
            if not normalized_tags_names:
                return []

            post_list = (
                select(PostORM)
                .options(
                    selectinload(PostORM.tags),
                    joinedload(PostORM.author),
                ).where(PostORM.tags.any(func.lower(TagORM.name).in_(normalized_tags_names)))
                .order_by(PostORM.id.asc())
            )

            posts = self.db.execute(post_list).scalars().all()
            
            return posts
        
    def ensure_author(self,name:str,email:str)->AuthorORM:
        
        author_obj= self.db.execute(select(AuthorORM).where(AuthorORM.email == email)).scalar_one_or_none()
        
        if author_obj:
            return author_obj
                
        author_obj=AuthorORM(name=name,email=email)
        self.db.add(author_obj)
        self.db.flush()
        return author_obj
        
    def ensure_tags(self, name:str)->TagORM:
        
        tag_obj=self.db.execute(select(TagORM).where(TagORM.name.ilike(name))).scalar_one_or_none()
        if tag_obj:
            return tag_obj
        
        tag_obj= TagORM(name=name)
        self.db.add(tag_obj)
        self.db.flush()
            
        return tag_obj
    
    def create_post(self,title:str,content:str,author:List[dict],tags:List[dict])->PostORM:
        author_obj=None
        
        if author:
            author_obj=self.ensure_author(author['username'],author['email'])
        
        post= PostORM(title=title, content=content, author=author_obj)
        
        for tag in tags:
            tag_obj= self.ensure_tags(tag['name'])
            post.tags.append(tag_obj)
            
        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)
        
        return post
    
    def delete_post(self,post:PostORM)->None:
        self.db.delete(post)
        
    
    
    def update_post(self,post:PostORM,updates:Dict)->PostORM:
        
        for key,value in updates.items():
            setattr(post,key,value)
            
        self.db.add(post)
        
        return post
        
    
        
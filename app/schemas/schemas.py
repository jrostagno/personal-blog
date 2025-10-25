


from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Tag(BaseModel):
    name:str=Field(...,min_length=2, max_length=30,description="Nombre de la etiqueta")
    model_config=ConfigDict(from_attributes=True)
    

class Author(BaseModel):
    name:str
    email:EmailStr
    model_config=ConfigDict(from_attributes=True)
    
class PostBase(BaseModel):
    title:str
    content:str
    tags:Optional[List[Tag]]=Field(default_factory=list)
    author:Optional[Author]=None
    model_config=ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title:str=Field(
        ...,min_length=2, 
        max_length=100,
        description="Titulo del post", 
        examples=['Este es el titulo del post'] )
    
    content:Optional[str]=Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post minimo 10 caracteres",
        examples=["Este es un contenido sobre programacion"])
    
    tags:List[Tag]=Field(default_factory=list) # []
    
    author:Optional[Author]=None
    
    
class PostPublic(PostBase):
    id:int
    model_config=ConfigDict(from_attributes=True)
    

     
    

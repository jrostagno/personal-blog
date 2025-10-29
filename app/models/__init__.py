# Importar todos los modelos para que estén disponibles
from .author import AuthorORM
from .tag import TagORM
from .post import PostORM,post_tags



__all__ = ["AuthorORM", "PostORM", "TagORM", "post_tags"]

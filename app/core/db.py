from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")


engine= create_engine(DATABASE_URL, echo=True, future=True) ## echo=True , muestra el SQL ejecutado para que lo veamos enla terminal, Future=True, le decimos que queremos ocupar la sintaxis moderna de SQlAlchemy

SessionLocal= sessionmaker(bind=engine,autoflush=False,autocommit=False,class_=Session,expire_on_commit=False) # autoflush lo que hace es no enviar cambios hasta hacer el Commit si esta en FALSE, si queres que se guarden de forma inmediata, lo mismo autocomit=False , hace que se tenga un control explicito sobrel el commit


class Base(DeclarativeBase):
    pass

# Funcion con la cual Creamos la session, y la cerramos cuando no la usammos 
def get_db()->Session:
    db=SessionLocal()
    try:
        yield db ## FASTAPI Expera una dependencia de tipo generadora, es como que le deceimos te entrego esta DB y cuando termines de hacer lo q tengas q hacer y ahi Cirreo la DB.
    finally:
        db.close()


import pytest
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, get_db
from app.core.security import get_current_user
from app.main import app
from app.models.author import AuthorORM
from app.models.post import PostORM


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # o en memoria: "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)  # No se envian cambios hasta q no se hace el commit


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# Override de dependencia de FastAPI


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_current_user():
    return {
        "email": "javier@mail.com",
        "username": "javier",
        "id": 1,  # por si lo usás
    }


app.dependency_overrides[get_current_user] = override_current_user
# correr test


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


def test_get_posts_empty(db_session):
    response = client.get("/posts")
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_create_post(db_session):

    payload = {
        "title": "Mi primer post",
        "content": "Contenido del primer post de TEST",
        "tags": [{"name": "python"}, {"name": "fastapi"}],
        "image_url": "https://example.com/img.png",
        # "author_id": author.id,
    }
    # res_create = client.post("/posts", json=payload)

    res_create = client.post("/posts", data=payload)

    rest_get_post_id = client.get(f"/posts/{1}")

    assert res_create.status_code == 201

    data = res_create.json()
    assert data["title"] == "Mi primer post"
    assert data["content"] == "Contenido del primer post de TEST"

    post_id = data["id"]

    rest_get_post_id = client.get(f"/posts/{post_id}")
    assert rest_get_post_id.status_code == 200

    data_post = rest_get_post_id.json()
    assert data_post["id"] == post_id
    assert data_post["title"] == "Mi primer post"
    assert data_post["content"] == "Contenido del primer post de TEST"

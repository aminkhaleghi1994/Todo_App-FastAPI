from fastapi.testclient import TestClient
from core.database import Base, create_engine, sessionmaker, get_db
from sqlalchemy import StaticPool
from main import app
import pytest
from tasks.models import TaskModel
from users.models import UserModel


SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

engine = create_engine(
       SQLALCHEMY_DATABASE_URI,
       connect_args={"check_same_thread": False},
       poolclass=StaticPool
   )

TestSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope='module')
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope='module', autouse=True)
def override_dependencies(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope='session', autouse=True)
def tear_up_and_down_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='function')
def anonymous_client():
    client = TestClient(app)
    yield client

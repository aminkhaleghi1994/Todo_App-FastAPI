from fastapi.testclient import TestClient
from core.database import Base, create_engine, sessionmaker, get_db
from sqlalchemy import StaticPool
from main import app
import pytest
from app.tasks.models import TaskModel
from app.users.models import UserModel
from faker import Faker
from app.auth.jwt_auth import generate_access_token


fake = Faker()

SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

engine = create_engine(
       SQLALCHEMY_DATABASE_URI,
       connect_args={"check_same_thread": False},
       poolclass=StaticPool
   )

TestSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope='package')
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


@pytest.fixture(scope='function')
def auth_client(db_session):
    client = TestClient(app)
    user = db_session.query(UserModel).filter_by(username="test_user").first()
    access_token = generate_access_token(user.id)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client


@pytest.fixture(scope='package', autouse=True)
def generate_mock_data(db_session):
    user = UserModel(username="test_user")
    user.set_password("123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    task_list = []
    for _ in range(10):
        task_list.append(
            TaskModel(
                user_id=user.id,
                title=fake.sentence(nb_words=6),
                description=fake.text(),
                is_completed=fake.boolean(),
            )
        )
    db_session.add_all(task_list)
    db_session.commit()
    print(f"added 10 Task For User with User_id: {user.id}")

@pytest.fixture(scope='function')
def random_task(db_session):
    user = db_session.query(UserModel).filter_by(username="test_user").first()
    task = db_session.query(TaskModel).filter_by(user_id=user.id).first()
    return task

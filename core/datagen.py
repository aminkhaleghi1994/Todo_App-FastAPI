from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.users.models import UserModel
from app.tasks.models import TaskModel
from faker import Faker


fake = Faker()


def seed_users(db: SessionLocal):
    user = UserModel(username=fake.user_name())
    user.set_password("123456789")
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User Created Successfully: {user.username}")
    return user


def seed_tasks(db: SessionLocal, user: UserModel, count=10):
    task_list = []
    for _ in range(count):
        task_list.append(
            TaskModel(
                user_id=user.id,
                title=fake.sentence(nb_words=6),
                description=fake.text(),
                is_completed=fake.boolean(),
            )
        )
    db.add_all(task_list)
    db.commit()
    print(f"added {count} Task For User with User_id: {user.id}")


def main():
    db = SessionLocal()
    try:
        user = seed_users(db)
        seed_tasks(db, user)
    finally:
        db.close()


if __name__ == "__main__":
    main()

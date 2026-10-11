from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task


def find_by_owner(db: Session, owner_id: int) -> list[Task]:
    stmt = select(Task).where(Task.owner_id == owner_id).order_by(Task.created_at.desc(), Task.id.desc())
    return list(db.scalars(stmt))


def find_by_id_and_owner(db: Session, task_id: int, owner_id: int) -> Task | None:
    return db.scalar(select(Task).where(Task.id == task_id, Task.owner_id == owner_id))


def save(db: Session, task: Task) -> Task:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()

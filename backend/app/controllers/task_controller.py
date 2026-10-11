from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.task import Task
from app.models.user import User
from app.services import task_service
from app.views.task import TaskRequest


def list_tasks(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[Task]:
    """List the current user's tasks, newest first."""
    return task_service.find_all_for_user(db, user)


def get_task(
    task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Task:
    return task_service.find_one(db, task_id, user)


def create_task(
    data: TaskRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Task:
    return task_service.create(db, data, user)


def update_task(
    task_id: int,
    data: TaskRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Task:
    return task_service.update(db, task_id, data, user)


def delete_task(
    task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> None:
    task_service.delete(db, task_id, user)

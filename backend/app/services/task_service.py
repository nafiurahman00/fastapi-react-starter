"""Business logic for tasks, always scoped to the logged-in user."""
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.models.task import Task
from app.models.user import User
from app.repositories import task_repository
from app.views.task import TaskRequest


def find_all_for_user(db: Session, user: User) -> list[Task]:
    return task_repository.find_by_owner(db, user.id)


def find_one(db: Session, task_id: int, user: User) -> Task:
    return _require_owned_task(db, task_id, user)


def create(db: Session, data: TaskRequest, user: User) -> Task:
    task = Task(
        title=data.title,
        description=data.description,
        completed=data.completed,
        owner_id=user.id,
    )
    return task_repository.save(db, task)


def update(db: Session, task_id: int, data: TaskRequest, user: User) -> Task:
    task = _require_owned_task(db, task_id, user)
    task.title = data.title
    task.description = data.description
    task.completed = data.completed
    return task_repository.save(db, task)


def delete(db: Session, task_id: int, user: User) -> None:
    task_repository.delete(db, _require_owned_task(db, task_id, user))


def _require_owned_task(db: Session, task_id: int, user: User) -> Task:
    """Load a task only if it belongs to this user; otherwise 404."""
    task = task_repository.find_by_id_and_owner(db, task_id, user.id)
    if task is None:
        raise ResourceNotFoundError("Task", task_id)
    return task

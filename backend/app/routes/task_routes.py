from fastapi import APIRouter, Depends, status

from app.controllers import task_controller
from app.core.dependencies import bearer_scheme
from app.routes import paths
from app.views.task import TaskResponse

# Every task route needs a valid JWT; `bearer_scheme` also shows the lock icon
# and "Authorize" button in Swagger UI. (get_current_user enforces it.)
router = APIRouter(
    prefix=paths.TASKS, tags=["Tasks"], dependencies=[Depends(bearer_scheme)]
)

router.add_api_route(
    "", task_controller.list_tasks, methods=["GET"], response_model=list[TaskResponse]
)
router.add_api_route(
    paths.TASK_BY_ID, task_controller.get_task, methods=["GET"], response_model=TaskResponse
)
router.add_api_route(
    "", task_controller.create_task, methods=["POST"],
    response_model=TaskResponse, status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    paths.TASK_BY_ID, task_controller.update_task, methods=["PUT"], response_model=TaskResponse
)
router.add_api_route(
    paths.TASK_BY_ID, task_controller.delete_task, methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
)

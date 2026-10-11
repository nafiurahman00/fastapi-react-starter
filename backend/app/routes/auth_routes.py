from fastapi import APIRouter, status

from app.controllers import auth_controller
from app.routes import paths
from app.views.auth import AuthResponse

router = APIRouter(prefix=paths.AUTH, tags=["Auth"])

router.add_api_route(
    paths.REGISTER, auth_controller.register, methods=["POST"],
    response_model=AuthResponse, status_code=status.HTTP_201_CREATED,
    summary="Create an account",
)
router.add_api_route(
    paths.LOGIN, auth_controller.login, methods=["POST"],
    response_model=AuthResponse, summary="Log in",
)

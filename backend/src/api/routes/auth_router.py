from fastapi import APIRouter
from src.api.controllers import auth_controller
from src.api.schemas.auth import TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])

router.add_api_route("/register", auth_controller.register, methods=["POST"], response_model=TokenResponse)
router.add_api_route("/login",    auth_controller.login,    methods=["POST"], response_model=TokenResponse)
router.add_api_route("/refresh",  auth_controller.refresh,  methods=["POST"], response_model=TokenResponse)
router.add_api_route("/logout",   auth_controller.logout,   methods=["POST"])
router.add_api_route("/me",       auth_controller.me,       methods=["GET"],  response_model=UserResponse)

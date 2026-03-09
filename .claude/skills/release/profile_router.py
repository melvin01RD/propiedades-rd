from fastapi import APIRouter
from src.api.controllers import profile_controller
from src.api.schemas.profile_schemas import (
    AgentProfileResponse,
    OwnerProfileResponse,
)

agents_router = APIRouter(prefix="/agents", tags=["Agentes"])
owners_router = APIRouter(prefix="/owners", tags=["Propietarios"])

# ── Agent ──────────────────────────────────────────────────────────────────
agents_router.add_api_route("/me", profile_controller.get_agent_me,    methods=["GET"],  response_model=AgentProfileResponse)
agents_router.add_api_route("/me", profile_controller.create_agent_me, methods=["POST"], response_model=AgentProfileResponse, status_code=201)
agents_router.add_api_route("/me", profile_controller.update_agent_me, methods=["PUT"],  response_model=AgentProfileResponse)

# ── Owner ──────────────────────────────────────────────────────────────────
owners_router.add_api_route("/me", profile_controller.get_owner_me,    methods=["GET"],  response_model=OwnerProfileResponse)
owners_router.add_api_route("/me", profile_controller.create_owner_me, methods=["POST"], response_model=OwnerProfileResponse, status_code=201)
owners_router.add_api_route("/me", profile_controller.update_owner_me, methods=["PUT"],  response_model=OwnerProfileResponse)

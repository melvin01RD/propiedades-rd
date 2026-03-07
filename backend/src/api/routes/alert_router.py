import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.dependencies import get_db, get_current_user
from src.persistence.models.user import User
from src.services.alert_service import alert_service
from src.api.schemas.alert_schemas import AlertCreate, AlertUpdate, AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alertas"])


@router.get(
    "",
    response_model=list[AlertResponse],
    summary="Mis alertas de búsqueda",
)
async def get_my_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await alert_service.get_my_alerts(db, current_user.id)


@router.post(
    "",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear alerta de búsqueda",
)
async def create_alert(
    data: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await alert_service.create(db, data, current_user.id)


@router.put(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Actualizar alerta",
)
async def update_alert(
    alert_id: uuid.UUID,
    data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await alert_service.update(db, alert_id, data, current_user)


@router.delete(
    "/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar alerta",
)
async def delete_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await alert_service.delete(db, alert_id, current_user)

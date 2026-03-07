import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.models.user import User
from src.persistence.repositories.alert_repository import alert_repository
from src.api.schemas.alert_schemas import AlertCreate, AlertUpdate


class AlertService:

    async def get_my_alerts(self, db: AsyncSession, user_id: uuid.UUID):
        return await alert_repository.get_by_user(db, user_id)

    async def create(self, db: AsyncSession, data: AlertCreate, user_id: uuid.UUID):
        payload = {
            "name":    data.name,
            "filters": data.filters.model_dump(exclude_none=True),
        }
        return await alert_repository.create(db, user_id, payload)

    async def update(
        self, db: AsyncSession, alert_id: uuid.UUID, data: AlertUpdate, current_user: User
    ):
        alert = await self._get_or_404(db, alert_id)
        self._assert_owner(alert, current_user)
        payload = data.model_dump(exclude_unset=True)
        if "filters" in payload and payload["filters"] is not None:
            payload["filters"] = data.filters.model_dump(exclude_none=True)
        return await alert_repository.update(db, alert, payload)

    async def delete(
        self, db: AsyncSession, alert_id: uuid.UUID, current_user: User
    ) -> None:
        alert = await self._get_or_404(db, alert_id)
        self._assert_owner(alert, current_user)
        await alert_repository.delete(db, alert)

    async def _get_or_404(self, db: AsyncSession, alert_id: uuid.UUID):
        alert = await alert_repository.get_by_id(db, alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alerta no encontrada",
            )
        return alert

    def _assert_owner(self, alert, current_user: User) -> None:
        if alert.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para modificar esta alerta",
            )


alert_service = AlertService()

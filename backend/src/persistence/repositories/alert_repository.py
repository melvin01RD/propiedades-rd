import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.persistence.models.alert import Alert


class AlertRepository:

    async def get_by_id(self, db: AsyncSession, alert_id: uuid.UUID) -> Alert | None:
        return await db.get(Alert, alert_id)

    async def get_by_user(self, db: AsyncSession, user_id: uuid.UUID) -> list[Alert]:
        result = await db.execute(
            select(Alert)
            .where(Alert.user_id == user_id)
            .order_by(Alert.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, user_id: uuid.UUID, data: dict) -> Alert:
        alert = Alert(user_id=user_id, **data)
        db.add(alert)
        await db.flush()
        await db.refresh(alert)
        return alert

    async def update(self, db: AsyncSession, alert: Alert, data: dict) -> Alert:
        for key, value in data.items():
            setattr(alert, key, value)
        await db.flush()
        await db.refresh(alert)
        return alert

    async def delete(self, db: AsyncSession, alert: Alert) -> None:
        await db.delete(alert)
        await db.flush()


alert_repository = AlertRepository()

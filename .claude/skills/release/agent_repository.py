import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.persistence.models.agent import Agent


class AgentRepository:

    async def get_by_user_id(self, db: AsyncSession, user_id: uuid.UUID) -> Agent | None:
        result = await db.execute(
            select(Agent)
            .options(selectinload(Agent.user))
            .where(Agent.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, user_id: uuid.UUID, first_name: str, last_name: str, **kwargs) -> Agent:
        agent = Agent(user_id=user_id, first_name=first_name, last_name=last_name, **kwargs)
        db.add(agent)
        await db.flush()
        await db.refresh(agent)
        return agent

    async def update(self, db: AsyncSession, agent: Agent, **kwargs) -> Agent:
        for field, value in kwargs.items():
            if hasattr(agent, field) and value is not None:
                setattr(agent, field, value)
        await db.flush()
        await db.refresh(agent)
        return agent


agent_repository = AgentRepository()

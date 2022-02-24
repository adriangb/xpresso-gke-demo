from pydantic import BaseModel

from app.db.connection import ConnectionHealth


class DatabaseHealth(BaseModel):
    connected: bool


class Health(BaseModel):
    db: DatabaseHealth


async def health(db_health: ConnectionHealth) -> Health:
    return Health.construct(
        db=DatabaseHealth.construct(connected=await db_health.is_connected())
    )

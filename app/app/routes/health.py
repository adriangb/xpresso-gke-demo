from pydantic import BaseModel

from app.db.connection import InjectConnectionHealth


class DatabaseHealth(BaseModel):
    connected: bool


class Health(BaseModel):
    db: DatabaseHealth


async def health(db_health: InjectConnectionHealth) -> Health:
    """Verify that the app is responding to requests and connected to the database"""
    return Health.construct(
        db=DatabaseHealth.construct(connected=await db_health.is_connected())
    )

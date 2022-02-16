from app.db.connection import ConnectionHealth
from pydantic import BaseModel
from xpresso import Path


class DatabaseHealth(BaseModel):
    connected: bool


class Health(BaseModel):
    db: DatabaseHealth


async def health(db_health: ConnectionHealth) -> Health:
    """Verify that the app is responding to requests and connected to the database"""
    return Health(db=DatabaseHealth(connected=await db_health.is_connected()))


health_pathitem = Path("/health", get=health)
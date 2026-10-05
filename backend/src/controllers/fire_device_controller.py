from fastapi import Depends, Query
from sqlalchemy.orm import Session

from src.database.session import get_session
from src.middlewares.rbac_middleware import require_supervisor
from src.services.fire_device_service import FireDeviceService
from src.types.fire_device_payload import FireDevicePayload


def list_fire_device(
    building_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
):
    return FireDeviceService(session).list(building_id=building_id)


def create_fire_device(
    payload: FireDevicePayload,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_supervisor),
):
    return FireDeviceService(session).create(payload, actor)

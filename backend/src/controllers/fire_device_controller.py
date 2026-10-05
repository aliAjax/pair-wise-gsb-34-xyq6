from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.constants.roles import ROLE_SUPERVISOR
from src.constructors.fire_device_factory import build_fire_device_list
from src.db.session import get_db
from src.middlewares.rbac_middleware import current_user, require_roles
from src.services.fire_device_service import FireDeviceService
from src.types.fire_device_payload import FireDeviceCreatePayload

router = APIRouter()


@router.get("")
def list_fire_device(
    building_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: dict = Depends(current_user),
):
    service = FireDeviceService(db)
    return build_fire_device_list(service.list(building_id=building_id))


@router.post("")
def create_fire_device(
    payload: FireDeviceCreatePayload,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(ROLE_SUPERVISOR)),
):
    # Controller 层包装：登记设备仅主管可操作。
    service = FireDeviceService(db)
    device = service.create(payload)
    db.commit()
    return build_fire_device_list([device])[0]

"""楼栋控制器：薄封装 service，异常由全局处理器统一包装。"""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.session import get_session
from src.middlewares.rbac_middleware import current_user, require_supervisor
from src.services.building_service import BuildingService
from src.types.building_payload import BuildingPayload


def list_building(session: Session = Depends(get_session)):
    return BuildingService(session).list()


def create_building(
    payload: BuildingPayload,
    session: Session = Depends(get_session),
    actor: dict = Depends(require_supervisor),
):
    return BuildingService(session).create(payload, actor)

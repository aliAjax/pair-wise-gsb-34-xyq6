from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.constructors.building_factory import build_building_list
from src.db.session import get_db
from src.middlewares.rbac_middleware import current_user
from src.services.building_service import BuildingService

router = APIRouter()


@router.get("")
def list_building(db: Session = Depends(get_db), user: dict = Depends(current_user)):
    service = BuildingService(db)
    return build_building_list(service.list())

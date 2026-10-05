from sqlalchemy import select
from sqlalchemy.orm import Session

from src.constructors.building_factory import create_building_response
from src.models.entities import Building
from src.repositories.building_repository import BuildingRepository
from src.services.audit_service import write_audit
from src.services.errors import NotFoundError
from src.types.building_payload import BuildingPayload


class BuildingService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = BuildingRepository(session)

    def list(self) -> list[dict]:
        return [create_building_response(b) for b in self.repo.find_all()]

    def create(self, payload: BuildingPayload, actor: dict) -> dict:
        building = Building(
            name=payload.name,
            campus=payload.campus,
            floor_count=payload.floor_count,
            fire_grade=payload.fire_grade,
            manager_id=payload.manager_id,
            address_code=payload.address_code,
        )
        self.repo.add(building)
        write_audit(
            self.session, actor, "Building.create", "Building", building.id,
            f"楼栋建档：{building.name}（{building.campus}）",
        )
        self.session.commit()
        return create_building_response(building)

    def require(self, building_id: int) -> Building:
        building = self.repo.get(building_id)
        if building is None:
            raise NotFoundError("BUILDING_NOT_FOUND")
        return building

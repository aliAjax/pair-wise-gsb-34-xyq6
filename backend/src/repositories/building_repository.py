from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.entities import Building


class BuildingRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_all(self) -> list[Building]:
        return list(self.session.scalars(select(Building).order_by(Building.id)))

    def get(self, building_id: int) -> Building | None:
        return self.session.get(Building, building_id)

    def add(self, building: Building) -> Building:
        self.session.add(building)
        self.session.flush()
        return building

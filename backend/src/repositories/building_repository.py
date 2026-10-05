from sqlalchemy.orm import Session

from src.models.building import Building


class BuildingRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self):
        return self.db.query(Building).order_by(Building.id.asc()).all()

    def get(self, building_id: int) -> Building | None:
        return self.db.get(Building, building_id)

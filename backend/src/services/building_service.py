from sqlalchemy.orm import Session

from src.repositories.building_repository import BuildingRepository


class BuildingService:
    def __init__(self, db: Session):
        self.repo = BuildingRepository(db)

    def list(self):
        return self.repo.find_all()

    def get(self, building_id: int):
        return self.repo.get(building_id)

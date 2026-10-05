from src.models.building import Building
from src.types.building_payload import BuildingResponse


def build_building_response(building: Building) -> BuildingResponse:
    return BuildingResponse.model_validate(building)


def build_building_list(buildings) -> list[BuildingResponse]:
    return [build_building_response(row) for row in buildings]

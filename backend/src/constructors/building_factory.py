"""楼栋 ORM 实体 -> 响应 DTO / 默认表单对象的构造器。"""

from src.models.entities import Building


def create_building_dto(building: Building | None = None, **overrides) -> dict:
    if building is None:
        row = {
            "id": 0,
            "name": "",
            "campus": "",
            "floor_count": 1,
            "fire_grade": "二级",
            "manager_id": None,
            "address_code": "",
        }
    else:
        row = {
            "id": building.id,
            "name": building.name,
            "campus": building.campus,
            "floor_count": building.floor_count,
            "fire_grade": building.fire_grade,
            "manager_id": building.manager_id,
            "address_code": building.address_code,
            "manager_name": building.manager.name if building.manager else "",
            "device_count": len(building.devices),
            "task_count": len(building.tasks),
        }
    row.update(overrides)
    return row


def create_building_form(**overrides) -> dict:
    return create_building_dto(None, **overrides)


def create_building_response(building: Building, **overrides) -> dict:
    return create_building_dto(building, **overrides)

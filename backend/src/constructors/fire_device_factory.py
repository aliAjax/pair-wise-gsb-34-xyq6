"""消防设备 ORM 实体 -> 响应 DTO / 默认表单对象的构造器。"""

from src.models.entities import FireDevice


def create_fire_device_dto(device: FireDevice | None = None, **overrides) -> dict:
    if device is None:
        row = {
            "id": 0,
            "building_id": 0,
            "device_code": "",
            "device_type": "HYDRANT",
            "floor": "1",
            "location_desc": "",
            "install_date": None,
            "status": "NORMAL",
            "next_maintenance_at": None,
        }
    else:
        row = {
            "id": device.id,
            "building_id": device.building_id,
            "building_name": device.building.name if device.building else "",
            "device_code": device.device_code,
            "device_type": device.device_type,
            "floor": device.floor,
            "location_desc": device.location_desc,
            "install_date": device.install_date,
            "status": device.status,
            "next_maintenance_at": device.next_maintenance_at,
            # 未结隐患数由 service 汇总后注入
            "open_hazard_count": overrides.pop("open_hazard_count", 0),
        }
    row.update(overrides)
    return row


def create_fire_device_form(**overrides) -> dict:
    return create_fire_device_dto(None, **overrides)


def create_fire_device_response(device: FireDevice, **overrides) -> dict:
    return create_fire_device_dto(device, **overrides)

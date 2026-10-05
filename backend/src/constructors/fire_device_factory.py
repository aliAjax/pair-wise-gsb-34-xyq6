from src.models.fire_device import FireDevice
from src.types.fire_device_payload import FireDeviceResponse


def build_fire_device_response(device: FireDevice) -> FireDeviceResponse:
    return FireDeviceResponse(
        id=device.id,
        building_id=device.building_id,
        device_code=device.device_code,
        device_type=device.device_type,
        floor=device.floor,
        location_desc=device.location_desc,
        install_date=device.install_date.isoformat() if device.install_date else None,
        status=device.status,
        next_maintenance_at=device.next_maintenance_at.isoformat() if device.next_maintenance_at else None,
    )


def build_fire_device_list(devices) -> list[FireDeviceResponse]:
    return [build_fire_device_response(row) for row in devices]

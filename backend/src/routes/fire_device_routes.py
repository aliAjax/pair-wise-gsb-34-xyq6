from fastapi import APIRouter

from src.controllers.fire_device_controller import create_fire_device, list_fire_device

router = APIRouter(prefix="/api/fire-device", tags=["FireDevice"])
router.get("", response_model=None)(list_fire_device)
router.post("", response_model=None)(create_fire_device)

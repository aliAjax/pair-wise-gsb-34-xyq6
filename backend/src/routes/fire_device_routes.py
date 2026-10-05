from fastapi import APIRouter

from src.controllers.fire_device_controller import router as controller_router

# 前缀在 include 时挂载，保证列表空路径在 /api/... 下直接生效（无 307）。
router = APIRouter(tags=['FireDevice'])
router.include_router(controller_router, prefix='/api/fire-device')

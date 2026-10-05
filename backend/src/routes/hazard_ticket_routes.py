from fastapi import APIRouter

from src.controllers.hazard_ticket_controller import router as controller_router

# 前缀在 include 时挂载，保证列表空路径在 /api/... 下直接生效（无 307）。
router = APIRouter(tags=['HazardTicket'])
router.include_router(controller_router, prefix='/api/hazard-ticket')

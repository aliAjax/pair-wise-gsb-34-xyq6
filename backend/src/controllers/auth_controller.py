from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.middlewares.rbac_middleware import current_user
from src.services.auth_service import AuthService
from src.types.auth_payload import LoginPayload

router = APIRouter()


@router.post("/login")
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(payload.username, payload.password)


@router.get("/me")
def me(db: Session = Depends(get_db), user: dict = Depends(current_user)):
    service = AuthService(db)
    return service.me(user["id"])


@router.get("/users")
def list_users(db: Session = Depends(get_db), user: dict = Depends(current_user)):
    service = AuthService(db)
    users = service.list_users()
    from src.constructors.user_factory import build_user_response

    return [build_user_response(row) for row in users]

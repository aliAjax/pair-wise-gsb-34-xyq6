from src.models.user import User
from src.types.auth_payload import UserResponse


def build_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        role=user.role,
    )

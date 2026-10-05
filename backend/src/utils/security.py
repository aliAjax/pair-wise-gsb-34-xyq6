import base64
import hashlib
import hmac
import json
import time

from src.config.settings import JWT_EXPIRE_MINUTES, JWT_SECRET

# 轻量 JWT（HS256）实现，避免依赖额外密码学库；校验仅依赖 hmac 常量时间比较。


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(signing_input: bytes) -> bytes:
    return hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()


def create_access_token(user_id: int, role: str, username: str = "") -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "role": role,
        "username": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRE_MINUTES * 60,
    }
    signing_input = _b64url(json.dumps(header, separators=(",", ":")).encode()) + "." + _b64url(
        json.dumps(payload, separators=(",", ":")).encode()
    )
    return signing_input + "." + _b64url(_sign(signing_input.encode()))


def decode_access_token(token: str) -> dict:
    try:
        header_part, payload_part, signature_part = token.split(".")
    except ValueError as exc:
        raise ValueError("token malformed") from exc
    signing_input = (header_part + "." + payload_part).encode()
    expected = _b64url(_sign(signing_input))
    if not hmac.compare_digest(expected, signature_part):
        raise ValueError("signature mismatch")
    payload = json.loads(_b64url_decode(payload_part))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("token expired")
    return payload


def hash_password(password: str) -> str:
    # 本地系统的口令仅做演示，用盐值 sha256，不引入第三方加密服务。
    return hashlib.sha256((password + ":fire-inspect").encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)

"""Dependencias de FastAPI: de aquí salen el contenedor y el usuario actual."""
from functools import lru_cache

from fastapi import Depends, HTTPException, Request

from majo.config import Settings
from majo.container import Container, build_container
from majo.domain.models import User


@lru_cache
def get_container() -> Container:
    return build_container(Settings())


def optional_user(request: Request, c: Container = Depends(get_container)) -> User | None:
    token = request.cookies.get("token")
    return c.auth.user_from_token(token) if token else None


def staff(user: User | None = Depends(optional_user)) -> User:
    if not user:
        raise HTTPException(303, headers={"Location": "/login"})
    return user


def admin_only(user: User = Depends(staff)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "Solo el administrador puede entrar aquí.")
    return user

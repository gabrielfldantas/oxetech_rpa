from fastapi import Depends, Header, HTTPException, Request, status
from loguru import logger
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

ROLE_HIERARCHY = {
    "admin": 4,
    "manager": 3,
    "seller": 2,
    "viewer": 1,
}

VALID_ROLES = set(ROLE_HIERARCHY.keys())


def get_current_user(
    request: Request,
    x_api_key: str = Header(..., description="API Key do usuário"),
    db: Session = Depends(get_db),
) -> User:
    """Validate the API Key and return the authenticated user.

    Stores email in request.state for downstream logging. API key is never logged.
    """
    user = db.query(User).filter(User.api_key == x_api_key).first()
    if not user:
        logger.warning(
            "Auth failed | unknown api_key | path={}",
            request.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou usuário inativo",
        )
    if not user.active:
        logger.warning(
            "Auth failed | inactive user | email={} | path={}",
            user.email,
            request.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida ou usuário inativo",
        )

    request.state.user_email = user.email
    logger.debug(
        "Auth ok | email={} | role={} | path={}",
        user.email,
        user.role,
        request.url.path,
    )
    return user


def require_role(*allowed_roles: str):
    """Return a dependency that checks if the current user has one of the allowed roles."""

    def role_checker(
        request: Request,
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            logger.warning(
                "Authz denied | email={} | role={} | required={} | path={}",
                current_user.email,
                current_user.role,
                allowed_roles,
                request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Roles permitidas: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker

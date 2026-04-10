"""Lokal admin: innlogging og passord."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.auth_deps import get_current_admin
from app.api.deps import get_db
from app.models.admin_account import AdminAccount
from app.schemas.auth import AdminMeResponse, ChangePasswordRequest, LoginRequest, TokenResponse
from app.services import auth_admin as auth_svc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token = auth_svc.login_admin(db, data.username, data.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AdminMeResponse)
def me(admin: AdminAccount = Depends(get_current_admin)) -> AdminMeResponse:
    return AdminMeResponse(username=admin.username)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    admin: AdminAccount = Depends(get_current_admin),
) -> Response:
    auth_svc.change_admin_password(db, admin, data.current_password, data.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

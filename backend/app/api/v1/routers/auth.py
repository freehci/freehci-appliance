"""Lokal admin: innlogging, kontoer, passord og API-nøkler."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.auth_deps import get_current_admin
from app.api.deps import get_db
from app.core.config import get_settings
from app.models.admin_account import AdminAccount
from app.schemas.auth import (
    AdminAccountCreate,
    AdminAccountRead,
    AdminMeResponse,
    AdminResetPasswordRequest,
    AgentAuthHint,
    AgentConnectInfo,
    ApiTokenCreate,
    ApiTokenCreated,
    ApiTokenRead,
    ChangePasswordRequest,
    LoginRequest,
    TokenResponse,
)
from app.services import auth_admin as auth_svc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token = auth_svc.login_admin(db, data.username, data.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AdminMeResponse)
def me(admin: AdminAccount = Depends(get_current_admin)) -> AdminMeResponse:
    return AdminMeResponse(id=admin.id, username=admin.username)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    admin: AdminAccount = Depends(get_current_admin),
) -> Response:
    auth_svc.change_admin_password(db, admin, data.current_password, data.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/accounts", response_model=list[AdminAccountRead])
def list_accounts(
    db: Session = Depends(get_db),
    admin: AdminAccount = Depends(get_current_admin),
) -> list[AdminAccountRead]:
    return auth_svc.list_admin_accounts(db, admin)


@router.post("/accounts", response_model=AdminAccountRead)
def create_account(
    data: AdminAccountCreate,
    db: Session = Depends(get_db),
    admin: AdminAccount = Depends(get_current_admin),
) -> AdminAccountRead:
    return auth_svc.create_admin_account(db, admin, data.username, data.password)


@router.post("/accounts/{account_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_account_password(
    account_id: int,
    data: AdminResetPasswordRequest,
    db: Session = Depends(get_db),
    _: AdminAccount = Depends(get_current_admin),
) -> Response:
    auth_svc.reset_admin_password(db, account_id, data.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    admin: AdminAccount = Depends(get_current_admin),
) -> Response:
    auth_svc.delete_admin_account(db, admin, account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/tokens", response_model=list[ApiTokenRead])
def list_tokens(
    db: Session = Depends(get_db),
    _: AdminAccount = Depends(get_current_admin),
) -> list[ApiTokenRead]:
    return auth_svc.list_api_tokens(db)


@router.post("/tokens", response_model=ApiTokenCreated)
def create_token(
    data: ApiTokenCreate,
    db: Session = Depends(get_db),
    admin: AdminAccount = Depends(get_current_admin),
) -> ApiTokenCreated:
    return auth_svc.create_api_token(db, admin, data.name)


@router.delete("/tokens/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_token(
    token_id: int,
    db: Session = Depends(get_db),
    _: AdminAccount = Depends(get_current_admin),
) -> Response:
    auth_svc.delete_api_token(db, token_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/agent", response_model=AgentConnectInfo)
def agent_connect_info() -> AgentConnectInfo:
    """Offentlig hint til AI-agenter: OpenAPI, docs og hvordan Bearer-auth fungerer."""
    settings = get_settings()
    api = settings.api_v1_prefix.rstrip("/")
    return AgentConnectInfo(
        app_name=settings.app_name,
        api_prefix=api,
        openapi_url=f"{api}/openapi.json",
        docs_url=f"{api}/docs",
        auth=AgentAuthHint(
            type="http",
            header="Authorization: Bearer <token>",
            login_url=f"{api}/auth/login",
            tokens_url=f"{api}/auth/tokens",
            token_prefix=auth_svc.API_TOKEN_PREFIX,
            notes=[
                "Preferred for agents: create an IAM service account and issue an API token (fhci_…) on that account.",
                "Interactive users: set or reset their appliance password on the IAM user profile, then POST /auth/login.",
            ],
        ),
    )

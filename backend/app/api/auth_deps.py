from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.admin_account import AdminAccount


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> AdminAccount:
    """Krever at ApiAuthMiddleware har satt request.state.admin_id (gyldig JWT)."""
    aid = getattr(request.state, "admin_id", None)
    if aid is None:
        raise HTTPException(status_code=401, detail="ikke innlogget")
    row = db.get(AdminAccount, aid)
    if row is None:
        raise HTTPException(status_code=401, detail="sesjon ugyldig")
    return row

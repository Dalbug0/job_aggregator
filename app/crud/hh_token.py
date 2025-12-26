from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import RefreshToken
from app.models.hh_token import HHToken
from app.services.hh_auth import exchange_code_for_token


def save_hh_token(
    db: Session,
    user_id: int,
    code: str,
) -> HHToken:
    tokens = exchange_code_for_token(code)

    db_token = HHToken(
        user_id=user_id,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"],
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def save_refresh_token(
    db: Session, user_id: int, token: str, expires_at: datetime
) -> RefreshToken:
    db_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_refresh_token(db: Session, token: str) -> RefreshToken | None:
    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == token,
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )


def invalidate_user_refresh_tokens(db: Session, user_id: int) -> None:
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.commit()

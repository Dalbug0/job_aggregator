from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import RefreshToken


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

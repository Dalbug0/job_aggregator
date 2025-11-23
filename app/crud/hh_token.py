from sqlalchemy.orm import Session

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

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.logger import logger
from app.models.hh_token import HHToken
from app.services.hh_auth import exchange_code_for_token


def save_hh_token(
    db: Session,
    user_id: int,
    code: str,
) -> HHToken:
    logger.info(f"Exchanging authorization code for token for user_id: {user_id}")
    tokens = exchange_code_for_token(code)

    # Проверяем, существует ли токен для пользователя
    existing_token = db.query(HHToken).filter_by(user_id=user_id).first()
    
    if existing_token:
        # Обновляем существующий токен
        logger.info(f"Updating existing HH token for user_id: {user_id}")
        existing_token.access_token = tokens["access_token"]
        existing_token.refresh_token = tokens["refresh_token"]
        existing_token.expires_in = tokens["expires_in"]
        # Обновляем created_at для правильного вычисления expired
        existing_token.created_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing_token)
        logger.info(f"Successfully updated HH token for user_id: {user_id}")
        return existing_token
    else:
        # Создаем новый токен
        logger.info(f"Creating new HH token for user_id: {user_id}")
        db_token = HHToken(
            user_id=user_id,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=tokens["expires_in"],
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        logger.info(f"Successfully created HH token for user_id: {user_id}")
        return db_token

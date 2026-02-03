"""認証API"""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.database import get_db
from src.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from src.models.user import User
from src.schemas.auth import LoginRequest, LoginResponse, UserInfo, TokenRefreshResponse
from src.config import settings


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """ログイン"""
    # ユーザー検索
    result = await db.execute(
        select(User)
        .options(joinedload(User.store))
        .where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
        )

    # アカウントロックチェック
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="アカウントがロックされています。しばらく待ってからお試しください",
        )

    # パスワード検証
    if not verify_password(request.password, user.password_hash):
        # ログイン失敗回数をカウント
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.max_login_attempts:
            user.locked_until = datetime.utcnow() + timedelta(minutes=settings.lockout_minutes)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
        )

    # ログイン成功
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()

    # トークン生成
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserInfo(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role,
            store_id=str(user.store_id) if user.store_id else None,
            store_name=user.store.name if user.store else None,
        ),
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """トークンリフレッシュ"""
    payload = decode_token(refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なリフレッシュトークンです",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません",
        )

    # 新しいアクセストークン生成
    token_data = {"sub": str(user.id)}
    new_access_token = create_access_token(token_data)

    return TokenRefreshResponse(access_token=new_access_token)


@router.post("/logout")
async def logout():
    """ログアウト（クライアント側でトークン削除）"""
    return {"message": "ログアウトしました"}

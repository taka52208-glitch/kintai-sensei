"""認証API"""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.database import get_db
from src.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from src.core.auth import CurrentUser
from src.core.token_blacklist import blacklist_token
from src.models.user import User
from src.models.store import Organization
from src.schemas.auth import (
    LoginRequest, LoginResponse, SignupRequest, UserInfo,
    TokenRefreshRequest, TokenRefreshResponse, LogoutRequest, ChangePasswordRequest,
)
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


@router.post("/signup", response_model=LoginResponse)
async def signup(
    request: SignupRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """新規会員登録（組織＋管理者ユーザー同時作成）"""
    import uuid

    # メール重複チェック
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています",
        )

    # 組織を作成
    organization = Organization(
        id=str(uuid.uuid4()),
        name=request.organization_name,
    )
    db.add(organization)

    # 管理者ユーザーを作成
    user = User(
        id=str(uuid.uuid4()),
        organization_id=organization.id,
        store_id=None,
        email=request.email,
        password_hash=get_password_hash(request.password),
        name=request.name,
        role="admin",
        is_active=True,
    )
    db.add(user)

    await db.commit()
    await db.refresh(user)

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
            store_id=None,
            store_name=None,
        ),
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """トークンリフレッシュ"""
    payload = decode_token(request.refresh_token)

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
async def logout(request: LogoutRequest):
    """ログアウト（トークン無効化）"""
    if request.access_token:
        payload = decode_token(request.access_token)
        if payload and payload.get("exp"):
            blacklist_token(request.access_token, payload["exp"])
    if request.refresh_token:
        payload = decode_token(request.refresh_token)
        if payload and payload.get("exp"):
            blacklist_token(request.refresh_token, payload["exp"])
    return {"message": "ログアウトしました"}


@router.put("/password")
async def change_password(
    request: ChangePasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """パスワード変更"""
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="現在のパスワードが正しくありません",
        )

    current_user.password_hash = get_password_hash(request.new_password)
    await db.commit()

    return {"message": "パスワードを変更しました"}

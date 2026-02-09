"""ユーザーAPI"""

import secrets
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.database import get_db
from src.core.auth import AdminUser
from src.core.security import get_password_hash
from src.models.user import User, UserRole
from src.schemas.user import UserResponse, UserUpdate, UserInvite, InviteResponse, UserListResponse


router = APIRouter()


@router.get("", response_model=UserListResponse)
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
    page: int = 1,
    page_size: int = 20,
):
    """ユーザー一覧取得（管理者のみ）"""
    offset = (page - 1) * page_size

    # 総件数
    count_result = await db.execute(
        select(func.count())
        .select_from(User)
        .where(User.organization_id == current_user.organization_id)
    )
    total = count_result.scalar_one()

    # ユーザー取得
    result = await db.execute(
        select(User)
        .options(joinedload(User.store))
        .where(User.organization_id == current_user.organization_id)
        .offset(offset)
        .limit(page_size)
    )
    users = result.scalars().all()

    items = [
        UserResponse(
            id=str(u.id),
            email=u.email,
            name=u.name,
            role=u.role.value,
            store_id=str(u.store_id) if u.store_id else None,
            store_name=u.store.name if u.store else None,
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]

    return UserListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """ユーザー詳細取得（管理者のみ）"""
    result = await db.execute(
        select(User)
        .options(joinedload(User.store))
        .where(User.id == user_id, User.organization_id == current_user.organization_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role.value,
        store_id=str(user.store_id) if user.store_id else None,
        store_name=user.store.name if user.store else None,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/invite", response_model=InviteResponse)
async def invite_user(
    request: UserInvite,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """ユーザー招待（管理者のみ）"""
    # 既存ユーザーチェック
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています",
        )

    # 仮パスワード生成
    temp_password = secrets.token_urlsafe(12)

    user = User(
        organization_id=current_user.organization_id,
        store_id=UUID(request.store_id) if request.store_id else None,
        email=request.email,
        password_hash=get_password_hash(temp_password),
        name=request.email.split("@")[0],  # 仮名
        role=UserRole(request.role),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role.value,
        store_id=str(user.store_id) if user.store_id else None,
        store_name=None,
        is_active=user.is_active,
        created_at=user.created_at,
    )

    return InviteResponse(
        user=user_response,
        temporary_password=temp_password,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """ユーザー更新（管理者のみ）"""
    result = await db.execute(
        select(User)
        .options(joinedload(User.store))
        .where(User.id == user_id, User.organization_id == current_user.organization_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    if request.role is not None:
        user.role = UserRole(request.role)
    if request.store_id is not None:
        user.store_id = UUID(request.store_id) if request.store_id else None
    if request.is_active is not None:
        user.is_active = request.is_active

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role.value,
        store_id=str(user.store_id) if user.store_id else None,
        store_name=user.store.name if user.store else None,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """ユーザー削除（管理者のみ）"""
    result = await db.execute(
        select(User)
        .where(User.id == user_id, User.organization_id == current_user.organization_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="自分自身は削除できません")

    await db.delete(user)
    await db.commit()

    return {"message": "ユーザーを削除しました"}

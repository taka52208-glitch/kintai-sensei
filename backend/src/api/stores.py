"""店舗API"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.auth import AdminUser
from src.models.store import Store
from src.schemas.store import StoreResponse, StoreCreate, StoreUpdate, StoreListResponse


router = APIRouter()


@router.get("", response_model=StoreListResponse)
async def list_stores(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """店舗一覧取得（管理者のみ）"""
    result = await db.execute(
        select(Store)
        .where(Store.organization_id == current_user.organization_id)
        .order_by(Store.code)
    )
    stores = result.scalars().all()

    items = [
        StoreResponse(
            id=str(s.id),
            code=s.code,
            name=s.name,
            created_at=s.created_at,
        )
        for s in stores
    ]

    return StoreListResponse(items=items, total=len(items))


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """店舗詳細取得（管理者のみ）"""
    result = await db.execute(
        select(Store)
        .where(Store.id == store_id, Store.organization_id == current_user.organization_id)
    )
    store = result.scalar_one_or_none()

    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店舗が見つかりません")

    return StoreResponse(
        id=str(store.id),
        code=store.code,
        name=store.name,
        created_at=store.created_at,
    )


@router.post("", response_model=StoreResponse)
async def create_store(
    request: StoreCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """店舗作成（管理者のみ）"""
    # コード重複チェック
    result = await db.execute(
        select(Store)
        .where(
            Store.organization_id == current_user.organization_id,
            Store.code == request.code,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="この店舗コードは既に使用されています",
        )

    store = Store(
        organization_id=current_user.organization_id,
        code=request.code,
        name=request.name,
    )
    db.add(store)
    await db.commit()
    await db.refresh(store)

    return StoreResponse(
        id=str(store.id),
        code=store.code,
        name=store.name,
        created_at=store.created_at,
    )


@router.put("/{store_id}", response_model=StoreResponse)
async def update_store(
    store_id: UUID,
    request: StoreUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """店舗更新（管理者のみ）"""
    result = await db.execute(
        select(Store)
        .where(Store.id == store_id, Store.organization_id == current_user.organization_id)
    )
    store = result.scalar_one_or_none()

    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店舗が見つかりません")

    if request.code is not None:
        store.code = request.code
    if request.name is not None:
        store.name = request.name

    await db.commit()
    await db.refresh(store)

    return StoreResponse(
        id=str(store.id),
        code=store.code,
        name=store.name,
        created_at=store.created_at,
    )


@router.delete("/{store_id}")
async def delete_store(
    store_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """店舗削除（管理者のみ）"""
    result = await db.execute(
        select(Store)
        .where(Store.id == store_id, Store.organization_id == current_user.organization_id)
    )
    store = result.scalar_one_or_none()

    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="店舗が見つかりません")

    await db.delete(store)
    await db.commit()

    return {"message": "店舗を削除しました"}

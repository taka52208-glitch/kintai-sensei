"""初期データ作成スクリプト"""

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import settings
from src.core.security import get_password_hash
from src.models.store import Organization, Store
from src.models.user import User, UserRole


async def create_initial_data():
    """初期データを作成"""

    engine = create_async_engine(settings.database_url, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 既存データチェック
        result = await session.execute(select(Organization))
        if result.scalar_one_or_none():
            print("初期データは既に存在します")
            return

        # 組織作成
        org_id = str(uuid.uuid4())
        organization = Organization(
            id=org_id,
            name="デモ組織",
        )
        session.add(organization)

        # デモ店舗作成
        store_id = str(uuid.uuid4())
        store = Store(
            id=store_id,
            organization_id=org_id,
            code="STORE001",
            name="渋谷店",
        )
        session.add(store)

        # 管理者ユーザー作成
        admin_user = User(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            store_id=None,  # 管理者は全店舗アクセス
            email="admin@example.com",
            password_hash=get_password_hash("KintaiDev2026!"),
            name="管理者",
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        session.add(admin_user)

        # 店舗管理者ユーザー作成
        store_manager = User(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            store_id=store_id,
            email="store@example.com",
            password_hash=get_password_hash("KintaiDev2026!"),
            name="店長",
            role=UserRole.STORE_MANAGER.value,
            is_active=True,
        )
        session.add(store_manager)

        await session.commit()

        print("=" * 50)
        print("初期データを作成しました")
        print("=" * 50)
        print()
        print("【管理者アカウント】")
        print(f"  Email: admin@example.com")
        print(f"  Password: KintaiDev2026!")
        print()
        print("【店舗管理者アカウント】")
        print(f"  Email: store@example.com")
        print(f"  Password: KintaiDev2026!")
        print()
        print("【デモ店舗】")
        print(f"  コード: STORE001")
        print(f"  名前: 渋谷店")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(create_initial_data())

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import hash_password
from app.auth.tokens import create_access_token
from app.db.base import generate_uuid
from app.models.user import User


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=generate_uuid(),
        email="hari@unq.edu.ar",
        hashed_password=hash_password("seldon123"),
        role="director",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> User:
    user = User(
        id=generate_uuid(),
        email="admin@unq.edu.ar",
        hashed_password=hash_password("admin123"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_token(test_admin: User) -> str:
    return create_access_token(test_admin.id, test_admin.role)

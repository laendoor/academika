"""CLI interactivo para crear el primer usuario admin.

Uso:
    python -m app.seeds.create_admin      (via make seed-admin)

Funciona en dev y prod. El password nunca toca el repo.
Requiere que los seeds de referencia (make seed) ya hayan corrido.
"""

import asyncio
import getpass
import sys

from sqlalchemy import select

from app.auth.password import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User


async def main() -> None:
    print("=== Crear usuario admin ===")
    email = input("Email: ").strip()
    if not email:
        print("Error: el email no puede estar vacío.", file=sys.stderr)
        sys.exit(1)

    password = getpass.getpass("Contraseña: ")
    if not password:
        print("Error: la contraseña no puede estar vacía.", file=sys.stderr)
        sys.exit(1)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none() is not None:
            print(f"Error: ya existe un usuario con email '{email}'.", file=sys.stderr)
            sys.exit(1)

        user = User(email=email, hashed_password=hash_password(password), role="admin")
        session.add(user)
        await session.commit()

    print(f"Admin creado: {email}")


if __name__ == "__main__":
    asyncio.run(main())

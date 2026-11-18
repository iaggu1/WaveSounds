import asyncio
from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import delete

from backend.core.database import SessionLocal, engine
from backend.models.lead import Lead


async def remove_lead(email: str) -> None:
    try:
        async with SessionLocal() as session:
            await session.execute(delete(Lead).where(Lead.email == email))
            await session.commit()
    finally:
        await engine.dispose()


def main() -> int:
    raw_email = getpass("E-mail do titular (entrada oculta): ").strip().lower()
    try:
        email = str(TypeAdapter(EmailStr).validate_python(raw_email))
    except ValidationError:
        print("Formato de e-mail inválido.")
        return 2

    confirmation = input("Confirme a exclusão digitando EXCLUIR: ").strip()
    if confirmation != "EXCLUIR":
        print("Exclusão cancelada.")
        return 1

    asyncio.run(remove_lead(email))
    print("Solicitação processada. O lead foi removido se estava cadastrado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


import argparse
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from backend.core.database import SessionLocal, engine
from backend.models.lead import Lead


def positive_days(value: str) -> int:
    try:
        days = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("informe um número inteiro de dias") from error
    if days < 1:
        raise argparse.ArgumentTypeError("o período precisa ser de pelo menos 1 dia")
    return days


async def purge(older_than_days: int, execute: bool) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    try:
        async with SessionLocal() as session:
            query = select(func.count()).select_from(Lead).where(Lead.created_at < cutoff)
            matching_count = int(await session.scalar(query) or 0)
            if not execute:
                print(f"Prévia: {matching_count} lead(s) seriam removidos.")
                return 0

            result = await session.execute(delete(Lead).where(Lead.created_at < cutoff))
            await session.commit()
            deleted_count = int(result.rowcount or 0)
            print(f"Remoção concluída: {deleted_count} lead(s) removidos.")
            return 0
    finally:
        await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="Pré-visualiza ou remove leads antigos sem exibir PII.")
    parser.add_argument("--older-than-days", required=True, type=positive_days)
    parser.add_argument("--execute", action="store_true", help="confirma a exclusão; sem esta opção, apenas mostra a contagem")
    args = parser.parse_args()
    return asyncio.run(purge(args.older_than_days, args.execute))


if __name__ == "__main__":
    raise SystemExit(main())


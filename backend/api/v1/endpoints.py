import logging

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.core.database import get_session
from backend.core.security import log_email_event
from backend.models.lead import Lead
from backend.schemas.lead import LeadCreateRequest

router = APIRouter()
logger = logging.getLogger("forma.api")
settings = get_settings()
SUCCESS = {"status": "success", "message": "Acesso liberado. Verifique sua caixa de entrada."}


async def send_welcome_email(email: str, plan: str) -> None:
    if not settings.resend_api_key:
        logger.info("E-mail de boas-vindas não enviado: integração não configurada")
        return
    payload = {
        "from": settings.email_from,
        "to": [email],
        "subject": "Seu acesso à forma. está liberado",
        "html": f"<p>Seu acesso à forma. está liberado.</p><p>Plano selecionado: {plan}.</p>",
    }
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(8.0)) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.resend_api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
        log_email_event("E-mail de boas-vindas enviado", email)
    except (httpx.HTTPError, ValueError):
        log_email_event("Falha ao enviar e-mail de boas-vindas", email)


@router.post("/leads", status_code=status.HTTP_201_CREATED, responses={200: {"description": "Lead já cadastrado"}})
async def create_lead(
    payload: LeadCreateRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    if payload.company_website:
        return SUCCESS

    email = str(payload.email).strip().lower()
    try:
        existing = await session.scalar(select(Lead.id).where(Lead.email == email))
        if existing is not None:
            response.status_code = status.HTTP_200_OK
            return SUCCESS

        lead = Lead(email=email, plan_interest=payload.plan_interest)
        session.add(lead)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        response.status_code = status.HTTP_200_OK
        return SUCCESS
    except SQLAlchemyError:
        await session.rollback()
        logger.error("Falha ao persistir lead (database error)")
        raise HTTPException(status_code=500, detail="Não foi possível processar sua solicitação no momento.") from None

    background_tasks.add_task(send_welcome_email, email, payload.plan_interest)
    return SUCCESS


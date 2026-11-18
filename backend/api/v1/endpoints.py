import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.models.lead import Lead
from backend.models.outbox import EmailOutbox
from backend.schemas.lead import LeadCreateRequest

router = APIRouter()
logger = logging.getLogger("forma.api")
SUCCESS = {"status": "success", "message": "Acesso liberado. Verifique sua caixa de entrada."}

@router.post("/leads", status_code=status.HTTP_201_CREATED, responses={200: {"description": "Lead já cadastrado"}})
async def create_lead(
    payload: LeadCreateRequest,
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
        await session.flush()
        session.add(EmailOutbox(lead_id=lead.id, event_type="welcome"))
        await session.commit()
    except IntegrityError:
        await session.rollback()
        response.status_code = status.HTTP_200_OK
        return SUCCESS
    except SQLAlchemyError:
        await session.rollback()
        logger.error("Falha ao persistir lead (database error)")
        raise HTTPException(status_code=500, detail="Não foi possível processar sua solicitação no momento.") from None

    return SUCCESS


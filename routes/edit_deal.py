from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from crm_db import get_db, Deal
from fastapi import status as http_status

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/edit_deal/{deal_id}")
async def edit_deal_page(
    deal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        return {"error": "Deal not found"}

    return templates.TemplateResponse(
        "edit_deal.html",
        {"request": request, "deal": deal}
    )


@router.post("/edit_deal/{deal_id}")
async def update_deal(
    deal_id: int,
    title: str = Form(...),
    description: str = Form(""),
    amount: float = Form(...),
    currency: str = Form(...),
    status: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        return {"error": "Deal not found"}

    deal.title = title
    deal.description = description
    deal.amount = amount
    deal.currency = currency
    deal.status = status

    await db.commit()

    return RedirectResponse(
        url="/home",
        status_code=http_status.HTTP_303_SEE_OTHER
    )
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from crm_db import Base, engine, get_db, Client, User, Deal 
from schemas import ClientCreate
# from security import hash_password
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Optional

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()
    return user

@router.get("/create_deal")
async def register_form(request: Request):
    return templates.TemplateResponse(
        "create_deal.html",
        {"request": request}
    )

@router.post("/create_deal")
async def create_deal(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    currency: str = Form(default="UAH"),
    client_id: int = Form(...),
    status: str = Form("new"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    manager_id = current_user.id

    new_deal = Deal(
        title=title,
        description=description,
        amount=amount,
        currency=currency,
        client_id=client_id,
        manager_id=manager_id,
        status=status,
    )

    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)

    return RedirectResponse(url="/home/manager/clients", status_code=302)
    

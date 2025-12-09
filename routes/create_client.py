from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from crm_db import Base, engine, get_db, Client, User
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

@router.get("/create_client")
async def register_form(request: Request):
    return templates.TemplateResponse(
        "create_client.html",
        {"request": request}
    )

@router.post("/create_client")
async def create_client(
    request: Request,
    company_name: str = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    street: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    website: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user is None:
        return templates.TemplateResponse(
            "create_client.html",
            {"request": request, "error": "Потрібно увійти в акаунт"}
        )

    result = await db.execute(
        select(Client).where(Client.company_name == company_name)
    )
    existing_client = result.scalar_one_or_none()

    if existing_client:
        return templates.TemplateResponse(
            "create_client.html",
            {
                "request": request,
                "error": "Клієнт уже існує",
                "company_name": company_name,
                "country": country,
                "city": city,
                "street": street,
                "phone": phone,
                "email": email,
                "website": website,
            }
        )

    new_client = Client(
        company_name=company_name,
        country=country,
        city=city,
        street=street,
        phone=phone,
        email=email,
        website=website if website else None,
        manager_id=current_user.id  
    )

    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)

    return RedirectResponse(url="/home", status_code=302)

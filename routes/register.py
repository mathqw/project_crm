from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from crm_db import Base, engine, get_db, User
from schemas import UserRegister, UserOut
from security import hash_password
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@router.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )

@router.post("/register")
async def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    role: str = Form(...),
    db: AsyncSession = Depends(get_db)   
):

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Логин уже занят",
                "email": email,
                "first_name": first_name,
                "last_name": last_name
            }
        )

    new_user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=302)

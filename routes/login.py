from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from crm_db import Base, engine, get_db, User
# from security import hash_password
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@router.post("/login")
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неправильна пошта або пароль"}
        )

    if user.password_hash != password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неправильна пошта або пароль"}
        )

    response = RedirectResponse(url="/home", status_code=302)

    response.set_cookie(
        key="user_id",
        value=str(user.id),
        httponly=True 
    )

    return response


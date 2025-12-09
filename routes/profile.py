from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crm_db import get_db, User


router = APIRouter()
templates = Jinja2Templates(directory="templates")

async def get_current_user(request: Request, db: AsyncSession):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()
    return user

@router.get("/profile")
async def admin_home(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "title": "Профіль користувача",
        "user": user
    })
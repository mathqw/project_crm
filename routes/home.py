from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from . import templates

router = APIRouter()

@router.get("/")
async def home_page(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "title": "Головна сторінка"}
    )



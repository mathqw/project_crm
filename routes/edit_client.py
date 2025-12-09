from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from crm_db import get_db, Client

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/edit_client/{client_id}")
async def edit_client_page(
    client_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()

    if client is None:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Client not found"},
            status_code=404
        )

    return templates.TemplateResponse(
        "edit_client.html",
        {"request": request, "client": client}
    )

@router.post("/edit_client/{client_id}")
async def update_client(
    client_id: int,
    company_name: str = Form(...),
    country: str = Form(...),
    city: str = Form(...),
    street: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    website: str = Form(""),
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Client).where(Client.id == client_id)
    )
    client = result.scalar_one_or_none()

    if client is None:
        return templates.TemplateResponse(
            "error.html",
            {"request": {}, "message": "Client not found"},
            status_code=404
        )

    client.company_name = company_name
    client.country = country
    client.city = city
    client.street = street
    client.phone = phone
    client.email = email
    client.website = website

    await db.commit()

    return RedirectResponse(
        url="/home/manager/clients",
        status_code=status.HTTP_303_SEE_OTHER
    )

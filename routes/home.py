from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crm_db import get_db, User, Client, Deal


router = APIRouter()
templates = Jinja2Templates(directory="templates")

def check_role(user: User, allowed_roles: list[str]):
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="Недостатньо прав доступу"
        )

async def get_current_user(request: Request, db: AsyncSession):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == int(user_id)))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession):
    query = select(User).where(User.role.in_(["manager", "rop"]))
    result = await db.execute(query)
    return result.scalars().all()

async def get_clients(db: AsyncSession):
    query = select(Client).where(User.id == Client.manager_id)
    result = await db.execute(query)
    return result.scalars().all()

async def get_deals(db: AsyncSession):
    query = select(Deal).where(User.id == Deal.manager_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/home")
async def home(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)

    if not user:
        return RedirectResponse("/login")

    match user.role:
        case "admin":
            return RedirectResponse("/home/admin")
        case "manager":
            return RedirectResponse("/home/manager")
        case "rop":
            return RedirectResponse("/home/rop")
        case _:
            raise HTTPException(status_code=403, detail="Невідома роль")

@router.get("/home/admin")
async def admin_home(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    check_role(user, ["admin"])
    
    users = await get_users(db)

    return templates.TemplateResponse("home_admin.html", {
        "request": request,
        "title": "Адмін панель",
        "user": user,
        "users": users
    })

@router.get("/home/admin/reports")
async def kvp_reports(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    check_role(user, ["rop", "admin"])

    # Отримуємо всі угоди
    deals = await get_deals(db)
    clients = await get_clients(db)
    users = await get_users(db)

    # 1. Кількість угод по статусах
    status_counts = await db.execute(
        select(Deal.status, func.count(Deal.id))
        .group_by(Deal.status)
    )
    status_counts = dict(status_counts.all())  # {'new': 5, 'in_progress': 3, 'closed': 2}

    # 2. Загальна сума угод
    total_amount = await db.execute(
        select(func.sum(Deal.amount))
    )
    total_amount = total_amount.scalar() or 0

    # 3. Топ-5 менеджерів по обсягу продажів
    top_managers_query = await db.execute(
        select(User.first_name, User.last_name, func.sum(Deal.amount).label("total_sales"))
        .join(Deal, Deal.manager_id == User.id)
        .group_by(User.id)
        .order_by(desc("total_sales"))
        .limit(5)
    )
    top_managers = top_managers_query.all()  # [(first_name, last_name, total_sales), ...]

    return templates.TemplateResponse("reports.html", {
        "request": request,
        "title": "Панель КВП",
        "user": user,
        "status_counts": status_counts,
        "total_amount": total_amount,
        "top_managers": top_managers
    })

@router.get("/home/admin/all_clients")
async def admin_all_clients(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    check_role(user, ["rop", "admin"])

    return templates.TemplateResponse(
    "all_clients.html",
    {
        "request": request,
        "user": user,
        "clients": clients
    }
    )

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"status": "deleted"}

@router.delete("/delete_deal/{deal_id}")
async def delete_deal(deal_id: int, db: AsyncSession = Depends(get_db)):
    # отримуємо замовлення
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # видаляємо
    await db.delete(deal)
    await db.commit()

    # Повертаємо редірект на головну сторінку
    return RedirectResponse(url="/home", status_code=303)

@router.get("/home/manager")
async def manager_home(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    clients = await get_clients(db)
    deals = await get_deals(db)
    
    check_role(user, ["manager", "admin"])

    return templates.TemplateResponse("home_manager.html", {
        "request": request,
        "title": "Панель менеджера",
        "user": user,
        "deals": deals,
        "clients": clients
    })

@router.get("/home/manager/clients")
async def clients(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    check_role(user, ["manager", "admin"])

    clients = await get_clients(db)

    return templates.TemplateResponse(
        "clients.html",
        {
            "request": request,
            "user": user,
            "clients": clients
        }
    )

@router.get("/home/manager/deals")
async def deals(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    check_role(user, ["manager", "admin"])

    deals = await get_deals(db)
    clients = await get_clients(db)

    return templates.TemplateResponse(
        "deals.html",
        {
            "request": request,
            "user": user,
            "deals": deals,
            "clients": clients
        }
    )

@router.get("/home/rop")
async def kvp_home(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    check_role(user, ["rop", "admin"])

    deals = await get_deals(db)
    clients = await get_clients(db)
    users = await get_users(db)

    return templates.TemplateResponse("home_rop.html", {
        "request": request,
        "title": "Панель КВП",
        "user": user,
        "deals": deals,
        "clients": clients,
        "users": users
    })

from sqlalchemy import select, func, desc

@router.get("/home/rop/reports")
async def kvp_reports(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    check_role(user, ["rop", "admin"])

    deals = await get_deals(db)
    clients = await get_clients(db)
    users = await get_users(db)

    status_counts = await db.execute(
        select(Deal.status, func.count(Deal.id))
        .group_by(Deal.status)
    )
    status_counts = dict(status_counts.all()) 

    total_amount = await db.execute(
        select(func.sum(Deal.amount))
    )
    total_amount = total_amount.scalar() or 0

    top_managers_query = await db.execute(
        select(User.first_name, User.last_name, func.sum(Deal.amount).label("total_sales"))
        .join(Deal, Deal.manager_id == User.id)
        .group_by(User.id)
        .order_by(desc("total_sales"))
        .limit(5)
    )
    top_managers = top_managers_query.all()  

    return templates.TemplateResponse("reports.html", {
        "request": request,
        "title": "Панель КВП",
        "user": user,
        "status_counts": status_counts,
        "total_amount": total_amount,
        "top_managers": top_managers
    })

@router.get("/home/rop/all_clients")
async def admin_all_clients(request: Request, db: AsyncSession = Depends(get_db)):

    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")

    check_role(user, ["rop", "admin"])

    clients = await get_clients(db)

    return templates.TemplateResponse(
    "all_clients.html",
    {
        "request": request,
        "user": user,
        "clients": clients
    }
    )
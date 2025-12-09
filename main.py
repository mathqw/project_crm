from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from routes import home, register, login, profile, create_client, create_deal, edit_client, edit_deal

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home.router)
app.include_router(register.router)
app.include_router(login.router)
app.include_router(profile.router)
app.include_router(create_client.router)
app.include_router(create_deal.router)
app.include_router(edit_client.router)
app.include_router(edit_deal.router)

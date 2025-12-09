from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6)
    first_name: str
    last_name: str 
    role: str

class UserOut(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str

    class Config:
        from_attributes = True

class ClientCreate(BaseModel):
    company_name: str = Field(max_length=100)
    contry: str = Field(max_length=50)
    city: str = Field(max_length=50)
    street: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    email: str = Field(max_length=100)
    website: Optional[str] = Field(default=None, max_length=100)

class DealCreate(BaseModel):
    title: str = Field(..., max_length=150)
    description: str = Field(..., max_length=1000)

    amount: float
    currency: str = Field(default="UAH", max_length=10)

    client_id: int
    manager_id: int

    status: str = Field(default="new")  

class ClientUpdate(BaseModel):
    company_name: str
    country: str
    city: str
    street: str
    phone: str
    email: str
    website: str | None = None

class DeleteResponse(BaseModel):
    status: str
    detail: str | None = None


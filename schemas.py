from pydantic import BaseModel, Field

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

from pydantic import BaseModel, EmailStr
from typing import Optional


# Signup input
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "client"


# Login input
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# User output (response model)
class ShowUser(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        orm_mode = True


# File upload record response
class ShowFile(BaseModel):
    id: int
    filename: str
    uploaded_by: str

    class Config:
        orm_mode = True

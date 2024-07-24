from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    id: int
    
    class Config:
        from_attributes = True

class User(UserBase):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    full_name: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenRequest(BaseModel):
    email: str
    password: str

class TaskBase(BaseModel):
    id: int
    title: str
    user_id: int

class TaskList(TaskBase):
    title: str
    user_id: int
    created_date: datetime
    is_done: bool

class TaskCreate(BaseModel):
    title:str

class Task(BaseModel):
    id: int
    user: User
    title: str
    is_done: bool
    created_date: datetime
    updated_date: Optional[datetime] = None

    class Config:
        orm_mode = True

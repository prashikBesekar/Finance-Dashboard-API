from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from enum import Enum

class RoleEnum(str, Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"

class TypeEnum(str, Enum):
    income = "income"
    expense = "expense"

# ── Auth ──────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ── Users ─────────────────────────────────────────
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UpdateRoleRequest(BaseModel):
    role: RoleEnum

class UpdateStatusRequest(BaseModel):
    is_active: bool

# ── Financial Records ─────────────────────────────
class RecordCreate(BaseModel):
    amount: float
    type: TypeEnum
    category: str
    date: date
    notes: Optional[str] = None

class RecordUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TypeEnum] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

class RecordResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    type: TypeEnum
    category: str
    date: date
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from app.database import get_db
from app import models, schemas
from dotenv import load_dotenv
import os, uuid, hashlib, bcrypt

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

def hash_password(password: str) -> str:
    # use sha256 first to avoid bcrypt 72 byte limit
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return bcrypt.hashpw(hashed.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    plain_hashed = hashlib.sha256(plain.encode()).hexdigest()
    return bcrypt.checkpw(plain_hashed.encode(), hashed.encode())

def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))


@router.post("/register", response_model=schemas.UserResponse)
def register(body: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        password=hash_password(body.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    return {"access_token": create_token(user.id)}
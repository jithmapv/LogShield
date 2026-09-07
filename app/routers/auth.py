from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import Token, UserCreate
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> Token:
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(username=user_data.username, hashed_password=hash_password(user_data.password), role=user_data.role)
    db.add(user)
    db.commit()
    return Token(access_token=create_access_token(user.username, user.role))


@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_access_token(user.username, user.role))
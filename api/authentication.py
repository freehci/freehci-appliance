# api\authenrication.py

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.authentication import User, Token, verify_password, generate_jwt_token, get_password_hash


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dummy users list
users = [
    User(username="user1", password=get_password_hash("password1")),
    User(username="user2", password=get_password_hash("password2")),
]

# User-related functions
def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user(username)
    if user is None:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def get_user(username: str) -> Optional[User]:
    for user in users:
        if user.username == username:
            return user
    return None

# API routes
@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = generate_jwt_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

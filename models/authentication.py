# models/authentication.py

from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Constants
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# User class
class User(BaseModel):
    username: str
    password: str

# Token class
class Token(BaseModel):
    access_token: str
    token_type: str

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password-related functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT-related functions
def generate_jwt_token(user: User) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"username": user.username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from config import settings

router = APIRouter()

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

# In-memory user database simulation for clean standalone running
mock_user_db: Dict[str, Dict] = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", response_model=TokenSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegisterSchema):
    """Signs up a new remote-sensing operator on the system"""
    if user.username in mock_user_db:
        raise HTTPException(status_code=400, detail="Username already registered.")
    
    hashed_pwd = get_password_hash(user.password)
    mock_user_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "password_hash": hashed_pwd,
        "created_at": datetime.utcnow()
    }
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=TokenSchema)
@router.post("/login", response_model=TokenSchema)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticates operator credentials and issues secure OAuth2 JWT tokens"""
    user = mock_user_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates JWT access tokens against active credentials"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_41_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = mock_user_db.get(username)
    if user is None:
        raise credentials_exception
    return user

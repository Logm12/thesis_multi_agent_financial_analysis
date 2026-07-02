import os
import jwt
import datetime
import bcrypt
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, Field, EmailStr
from core.database import get_db_connection
from core.rate_limit import rate_limiter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "lumo_super_secret_key_2026_financial_analyzer")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# --- Pydantic Schemas ---
class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    full_name: str = Field(..., min_length=1, description="Full Name")

class UserLogin(BaseModel):
    email: str = Field(..., description="Email address or username")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: Optional[datetime.datetime] = None

class AuthResponse(BaseModel):
    status: str
    message: str
    user: UserResponse

# --- JWT Helpers ---
def create_access_token(user_id: str, email: str, role: str) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

# --- Dependency Injection Functions ---
oauth2_scheme = APIKeyCookie(name="access_token", auto_error=False)

async def get_current_user(request: Request, access_token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    if not access_token:
        # Check in headers if Cookie didn't match (for API testing / external clients)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.replace("Bearer ", "")
            
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in."
        )
        
    payload = verify_token(access_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or token is invalid. Please log in again."
        )
        
    user_id = payload.get("sub")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, full_name, role FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account not found."
                )
            return {
                "id": str(user[0]),
                "email": user[1],
                "full_name": user[2],
                "role": user[3]
            }

async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required."
        )
    return current_user

# --- Authentication Endpoints ---

@router.post("/register", response_model=AuthResponse, status_code=201, dependencies=[Depends(rate_limiter(5, 60))])
async def register(user_data: UserRegister):
    email = user_data.email.strip().lower()
    full_name = user_data.full_name.strip()
    
    # Simple validation checks
    if not email or not full_name:
        raise HTTPException(status_code=400, detail="Email and Full Name are required.")
    
    # Hash password using bcrypt
    password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if email exists
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An account with this email address already exists."
                )
            
            # Insert new user (default role: USER)
            cur.execute(
                "INSERT INTO users (email, full_name, password_hash, role) VALUES (%s, %s, %s, %s) RETURNING id, created_at",
                (email, full_name, password_hash, "USER")
            )
            res = cur.fetchone()
            user_id = str(res[0])
            created_at = res[1]
            
    return AuthResponse(
        status="success",
        message="Account registered successfully.",
        user=UserResponse(
            id=user_id,
            email=email,
            full_name=full_name,
            role="USER",
            created_at=created_at
        )
    )

@router.post("/login", response_model=AuthResponse, dependencies=[Depends(rate_limiter(5, 60))])
async def login(response: Response, credentials: UserLogin):
    email = credentials.email.strip().lower()
    password = credentials.password
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, full_name, password_hash, role, created_at FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password."
                )
            
            user_id = str(user[0])
            db_email = user[1]
            full_name = user[2]
            db_password_hash = user[3]
            role = user[4]
            created_at = user[5]
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), db_password_hash.encode('utf-8')):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password."
                )
                
    # Create JWT Token
    token = create_access_token(user_id, db_email, role)
    
    # Set HttpOnly Cookie
    # Check if we should disable secure=True in local development
    # If running in local environment without HTTPS, we set secure=False.
    # In production, secure should be True.
    is_prod = os.getenv("ENV", "development").lower() == "production" or os.getenv("RENDER") == "true"
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="none" if is_prod else "lax",
        secure=True if is_prod else False,
        path="/"
    )
    
    return AuthResponse(
        status="success",
        message="Logged in successfully.",
        user=UserResponse(
            id=user_id,
            email=db_email,
            full_name=full_name,
            role=role,
            created_at=created_at
        )
    )

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True
    )
    return {"status": "success", "message": "Logged out successfully."}

@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"]
    )

async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required."
        )
    return current_user

@router.get("/admin/stats")
async def get_admin_stats(admin_user: dict = Depends(get_admin_user)):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            total_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*), COALESCE(SUM(size_bytes), 0) FROM documents")
            row = cur.fetchone()
            total_docs = row[0]
            total_bytes = int(row[1])
            
            cur.execute("SELECT id, email, full_name, role, created_at FROM users ORDER BY created_at DESC")
            users_list = []
            for r in cur.fetchall():
                users_list.append({
                    "id": r[0],
                    "email": r[1],
                    "full_name": r[2],
                    "role": r[3],
                    "created_at": r[4].isoformat() if r[4] else None
                })
                
            cur.execute("SELECT d.id, d.filename, d.size_bytes, d.uploaded_at, u.email FROM documents d LEFT JOIN users u ON d.user_id = u.id ORDER BY d.uploaded_at DESC")
            docs_list = []
            for r in cur.fetchall():
                docs_list.append({
                    "id": r[0],
                    "filename": r[1],
                    "size_bytes": r[2],
                    "uploaded_at": r[3].isoformat() if r[3] else None,
                    "owner_email": r[4] or "System"
                })

    token_usage_data = [
        {"date": "2026-05-14", "prompt_tokens": 124000, "completion_tokens": 45000},
        {"date": "2026-05-15", "prompt_tokens": 145000, "completion_tokens": 52000},
        {"date": "2026-05-16", "prompt_tokens": 198000, "completion_tokens": 78000},
        {"date": "2026-05-17", "prompt_tokens": 160000, "completion_tokens": 61000},
        {"date": "2026-05-18", "prompt_tokens": 210000, "completion_tokens": 85000},
        {"date": "2026-05-19", "prompt_tokens": 250000, "completion_tokens": 98000},
        {"date": "2026-05-20", "prompt_tokens": 285000, "completion_tokens": 112000},
    ]

    return {
        "status": "success",
        "stats": {
            "total_users": total_users,
            "total_documents": total_docs,
            "total_storage_bytes": total_bytes,
        },
        "users": users_list,
        "documents": docs_list,
        "token_usage": token_usage_data
    }

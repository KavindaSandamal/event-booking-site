from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt, JWTError
from .utils import JWT_SECRET, JWT_ALGORITHM, verify_token, is_token_expired
import os
from .models import Base, User
from .schemas import UserCreate, Token, RefreshToken
from .utils import hash_password, verify_password, create_access_token, create_refresh_token
from .security import SecurityValidator, PasswordValidator, SecureUserCreate, SecureUserLogin
from .rate_limiter import check_rate_limit
from .security_middleware import SecurityHeadersMiddleware, RequestLoggingMiddleware, RateLimitMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
import time

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with connection pooling and retry mechanism
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,  # 30 minutes
    pool_timeout=30,
    connect_args={
        "connect_timeout": 10,
        "application_name": "auth_service"
    }
)
SessionLocal = sessionmaker(bind=engine)

# Create FastAPI app
app = FastAPI(title="Auth Service")

# Add CORS middleware
# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://event-booking.local", "https://event-booking.local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    # Add retry mechanism for database connection
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database connection attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                raise e

@app.get("/health")
@app.get("/auth/health")
def health_check():
    return {"status": "healthy", "service": "auth"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Database session error: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

@app.post("/register", response_model=Token)
@app.post("/auth/register", response_model=Token)
async def register(user_in: SecureUserCreate, request: Request, db: Session = Depends(get_db)):
    try:
        # Check rate limit
        await check_rate_limit(request, "register")
        
        # Additional security validation
        if not SecurityValidator.validate_input(user_in.username, "username"):
            raise HTTPException(status_code=400, detail="Invalid username format")
        
        if not SecurityValidator.validate_input(user_in.email, "email"):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Check for existing user
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user with secure password hashing
        user = User(
            email=user_in.email, 
            password_hash=PasswordValidator.hash_password(user_in.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutes in seconds
        }
    except Exception as e:
        print(f"Registration error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")

class LoginModel(BaseModel):
    email: str
    password: str

@app.post("/login", response_model=Token)
@app.post("/auth/login", response_model=Token)
async def login(credentials: SecureUserLogin, request: Request, db: Session = Depends(get_db)):
    try:
        # Check rate limit
        await check_rate_limit(request, "login")
        
        # Additional security validation
        if not SecurityValidator.validate_input(credentials.username, "username"):
            raise HTTPException(status_code=400, detail="Invalid username format")
        
        if not SecurityValidator.validate_input(credentials.password, "password"):
            raise HTTPException(status_code=400, detail="Invalid password format")
        
        user = db.query(User).filter(User.email == credentials.username).first()
        if not user or not PasswordValidator.verify_password(credentials.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60  # 30 minutes in seconds
        }
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/refresh", response_model=Token)
def refresh_token(refresh_token_req: RefreshToken, db: Session = Depends(get_db)):
    # Verify refresh token
    payload = verify_token(refresh_token_req.refresh_token, "refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Check if user still exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Create new tokens
    new_access_token = create_access_token(str(user.id))
    new_refresh_token = create_refresh_token(str(user.id))
    
    return {
        "access_token": new_access_token, 
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": 30 * 60  # 30 minutes in seconds
    }

@app.post("/verify")
def verify_token_endpoint(payload: dict):
    token = payload.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    
    # Check if token is expired
    if is_token_expired(token):
        raise HTTPException(status_code=401, detail="Token has expired")
    
    # Verify token
    token_payload = verify_token(token, "access")
    if not token_payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "user_id": token_payload.get("sub"),
        "exp": token_payload.get("exp"),
        "iat": token_payload.get("iat")
    }

@app.post("/logout")
def logout():
    # In a real application, you might want to blacklist the token
    # For now, we'll just return success
    return {"message": "Successfully logged out"}


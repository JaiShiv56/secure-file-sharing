from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app import models, schemas
from app.database import SessionLocal

router = APIRouter()

# JWT settings
SECRET_KEY = "supersecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token security scheme
oauth2_scheme = HTTPBearer()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utils: Password hash & verify
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT Token creator
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# FastAPI-Mail config (replace with your SMTP credentials)
conf = ConnectionConfig(
    MAIL_USERNAME="jaishivthakur56@gmail.com",        # ← Your Gmail address
    MAIL_PASSWORD="ijco hujc azik qgya",               # ← Your 16-digit App Password (no spaces!)
    MAIL_FROM="jaishivthakur56@gmail.com",            # ← Same Gmail
    MAIL_FROM_NAME="Secure File Sharing System",    # ← Display name (any string)
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

# Signup route with email verification email
@router.post("/signup", response_model=schemas.ShowUser, status_code=status.HTTP_201_CREATED)
async def signup(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw, role=user.role, is_verified=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create verification token (expires in 30 mins)
    token_data = {"sub": new_user.email, "exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    verify_url = f"http://localhost:8000/auth/verify-email?token={token}"
    print(f"🔗 Verification Link: {verify_url}")

    message = MessageSchema(
        subject="Verify your Email",
        recipients=[new_user.email],
        body=f"Please click this link to verify your email: {verify_url}",
        subtype="plain",
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

    return new_user

# Email verification endpoint
@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            return {"message": "Email already verified."}

        user.is_verified = True
        db.commit()
        return {"message": "Email verified successfully!"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

# Login route with check for email verification
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in.")

    token_data = {"sub": db_user.email, "role": db_user.role}
    token = create_access_token(data=token_data)
    return {"access_token": token, "token_type": "bearer"}

# Extract user from token (used in protected routes)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if not email or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"email": email, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

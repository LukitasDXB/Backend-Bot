from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models, schemas
from database import engine, SessionLocal, Base
from routes import football
from routes import Basketball  # ✅ make sure your file is named `Basketball.py`

# ✅ Step 1: Create FastAPI app
app = FastAPI(title="Sports Predictions API")

# ✅ Step 2: Include routers
app.include_router(football.router, prefix="/football", tags=["Football"])
app.include_router(Basketball.router, prefix="/basketball", tags=["Basketball"])

# ✅ Step 3: Create DB tables (only if not exists)
Base.metadata.create_all(bind=engine)

# ✅ Step 4: Add CORS middleware
origins = [
    "https://bettingbot.netlify.app",  # your frontend on Netlify
    "http://localhost:5173",           # local dev frontend (Vite default port)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # only allow these domains
    allow_credentials=True,
    allow_methods=["*"],        # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],        # allow all headers
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Signup
@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ✅ Login
@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {"message": "Login successful!"}

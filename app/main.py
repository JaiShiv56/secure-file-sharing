from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .auth import router as auth_router
from .file_ops import router as file_router

app = FastAPI()

# Create DB tables
models.Base.metadata.create_all(bind=engine)


# Root route
@app.get("/")
def root():
    return {"message": "Welcome to Secure File Sharing API"}

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(file_router, prefix="/files", tags=["File Operations"])

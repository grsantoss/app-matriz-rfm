import os
import json
import sys
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel
import uuid

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import PROJECT_NAME, BACKEND_URL, FRONTEND_URL, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION

# Import local modules
from rfm_service import RFMAnalysisService
from openai_service import OpenAIService
from database import create_tables

# Import routers
from routes.auth import router as auth_router
from routes.analysis import router as analysis_router
from routes.users import router as users_router

# Models
class AnalysisResult(BaseModel):
    analysis_id: str
    date_created: str
    summary: Dict[str, Any]
    insights: Optional[str] = None

class UserAnalysis(BaseModel):
    user_id: int
    analyses: List[AnalysisResult]

# Initialize FastAPI app
app = FastAPI(title=PROJECT_NAME)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Create storage directory if it doesn't exist
os.makedirs("storage/analysis_history", exist_ok=True)

# Serve static files (analysis results)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Include routers
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(users_router)

# Authentication dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return {"user_id": user_id}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "service": PROJECT_NAME}

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("Database tables created or verified.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5173, reload=True)
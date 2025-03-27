from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import sys
import os
import requests
import json
from pydantic import BaseModel
from typing import Optional

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config import AUTH_SERVICE_URL

# Auth router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Models
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class PasswordReset(BaseModel):
    email: str

class PasswordUpdate(BaseModel):
    token: str
    password: str

class TokenVerify(BaseModel):
    token: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Register a new user
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    try:
        # Forward request to Auth service
        response = requests.post(
            f"{AUTH_SERVICE_URL}/register",
            json=user.dict()
        )
        
        # Check response
        if response.status_code != 201:
            error_detail = response.json().get("detail", "Registration failed")
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail
            )
        
        return response.json()
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}"
        )

# Login and get token
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # Forward request to Auth service
        response = requests.post(
            f"{AUTH_SERVICE_URL}/login",
            data={
                "username": form_data.username,  # OAuth2 uses username, but we use email
                "password": form_data.password
            }
        )
        
        # Check response
        if response.status_code != 200:
            error_detail = response.json().get("detail", "Login failed")
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail
            )
        
        return response.json()
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}"
        )

# Forgot password
@router.post("/forgot-password")
async def forgot_password(reset_data: PasswordReset):
    try:
        # Forward request to Auth service
        response = requests.post(
            f"{AUTH_SERVICE_URL}/forgot-password",
            json=reset_data.dict()
        )
        
        # Check response
        if response.status_code != 200:
            error_detail = response.json().get("detail", "Password reset request failed")
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail
            )
        
        return response.json()
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}"
        )

# Reset password with token
@router.post("/reset-password")
async def reset_password(update_data: PasswordUpdate):
    try:
        # Forward request to Auth service
        response = requests.post(
            f"{AUTH_SERVICE_URL}/reset-password",
            json=update_data.dict()
        )
        
        # Check response
        if response.status_code != 200:
            error_detail = response.json().get("detail", "Password reset failed")
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail
            )
        
        return response.json()
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}"
        )

# Verify token
@router.post("/verify-token")
async def verify_token(token_data: TokenVerify):
    try:
        # Forward request to Auth service
        response = requests.post(
            f"{AUTH_SERVICE_URL}/verify-token",
            json=token_data.dict()
        )
        
        # Check response
        if response.status_code != 200:
            error_detail = response.json().get("detail", "Token verification failed")
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail
            )
        
        return response.json()
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Authentication service unavailable: {str(e)}"
        ) 
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import sys
import os
from typing import Dict, Any

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import JWT_SECRET, JWT_ALGORITHM

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Verify the JWT token and extract user information.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        Dictionary with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Extract user ID from token
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Return user information from token
        return {
            "user_id": int(user_id),
            "email": payload.get("email", ""),
            "name": payload.get("name", "")
        }
        
    except jwt.PyJWTError:
        raise credentials_exception 
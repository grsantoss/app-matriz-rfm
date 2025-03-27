from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config import JWT_SECRET, JWT_ALGORITHM

# Import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db, User, Analysis
from auth import get_current_user

# User router
router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me")
async def get_current_user_info(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about the current logged-in user.
    """
    try:
        # Query database for user details
        db_user = db.query(User).filter(User.id == user["user_id"]).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return user information (exclude password)
        return {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "created_at": db_user.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user information: {str(e)}")

@router.put("/me")
async def update_user_info(
    user_data: Dict[str, str],
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update information for the current logged-in user.
    """
    try:
        # Query database for user
        db_user = db.query(User).filter(User.id == user["user_id"]).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update allowed fields
        if "name" in user_data:
            db_user.name = user_data["name"]
        
        # Note: Email updates would typically require verification,
        # and password updates would be handled by the auth service
        
        # Commit changes
        db.commit()
        
        # Return updated user info
        return {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "created_at": db_user.created_at.isoformat(),
            "message": "User information updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user information: {str(e)}")

@router.get("/usage-stats")
async def get_usage_statistics(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for the current user.
    """
    try:
        # Get total number of analyses
        analysis_count = db.query(User).join(User.analyses).filter(User.id == user["user_id"]).count()
        
        # Get total storage usage
        storage_usage = db.query(func.sum(Analysis.file_size)).filter(
            Analysis.user_id == user["user_id"]
        ).scalar() or 0
        
        # Get statistics
        return {
            "total_analyses": analysis_count,
            "storage_usage_bytes": storage_usage,
            "storage_usage_mb": round(storage_usage / (1024 * 1024), 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving usage statistics: {str(e)}") 
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks, Body
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, List, Any, Optional
import os
import sys
import json
import pandas as pd
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.config import JWT_SECRET, JWT_ALGORITHM

# Import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rfm_service import RFMAnalysisService
from openai_service import OpenAIService
from database import get_db, Analysis, CustomerSegment
from auth import get_current_user

# Analysis router
router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# Create storage directory if it doesn't exist
os.makedirs("storage/analysis_history", exist_ok=True)

@router.post("/upload")
async def upload_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload customer transaction data for RFM analysis.
    """
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be CSV or Excel format")
    
    try:
        # Read file content
        contents = await file.read()
        
        # Save file temporarily
        temp_file_path = f"storage/temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(contents)
        
        # Read data into DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(temp_file_path)
        else:
            df = pd.read_excel(temp_file_path)
        
        # Delete temporary file
        os.remove(temp_file_path)
        
        # Validate data contains required columns
        required_columns = ['customer_id', 'transaction_id', 'transaction_date', 'transaction_amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Data is missing required columns: {', '.join(missing_columns)}"
            )
        
        # Create analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Create analysis record in database
        db_analysis = Analysis(
            analysis_id=analysis_id,
            user_id=user["user_id"],
            file_name=file.filename,
            file_size=len(contents),
            total_customers=len(df['customer_id'].unique())
        )
        
        db.add(db_analysis)
        db.commit()
        
        # Schedule background task for RFM analysis
        background_tasks.add_task(
            process_rfm_analysis,
            df=df,
            analysis_id=analysis_id,
            user_id=user["user_id"],
            db_session=db
        )
        
        return {
            "message": "Data uploaded successfully. Analysis is being processed.",
            "analysis_id": analysis_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

async def process_rfm_analysis(df: pd.DataFrame, analysis_id: str, user_id: int, db_session: Session):
    """
    Process RFM analysis as a background task.
    """
    try:
        # Create a new session for background task
        db = db_session
        
        # Create RFM analysis service
        rfm_service = RFMAnalysisService(df)
        
        # Perform RFM analysis
        summary = rfm_service.perform_full_analysis()
        
        # Update analysis record
        db_analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
        if db_analysis:
            db_analysis.total_customers = summary['total_customers']
            db.commit()
        
        # Save segment data to database
        for segment_name, segment_data in summary['segment_distribution'].items():
            db_segment = CustomerSegment(
                analysis_id=analysis_id,
                segment_name=segment_name,
                customer_count=segment_data['count'],
                percentage=segment_data['percentage'],
                avg_recency=segment_data['avg_recency'],
                avg_frequency=segment_data['avg_frequency'],
                avg_monetary=segment_data['avg_monetary'],
                total_revenue=segment_data['total_revenue'],
                revenue_percentage=segment_data['revenue_percentage']
            )
            db.add(db_segment)
        
        db.commit()
        
        # Generate insights using OpenAI
        insights = await OpenAIService.generate_rfm_insights(summary)
        
        # Create result object
        result = {
            "analysis_id": analysis_id,
            "date_created": datetime.now().isoformat(),
            "summary": summary,
            "insights": insights
        }
        
        # Save analysis results to file
        save_path = f"storage/analysis_history/{user_id}_{analysis_id}.json"
        with open(save_path, "w") as f:
            json.dump(result, f, indent=2)
            
    except Exception as e:
        print(f"Error in background processing: {e}")
        
        # Update analysis record to indicate error
        db_analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
        if db_analysis:
            db_analysis.has_error = True
            db_analysis.error_message = str(e)
            db.commit()
        
        # Save error details
        error_result = {
            "analysis_id": analysis_id,
            "date_created": datetime.now().isoformat(),
            "error": str(e)
        }
        
        save_path = f"storage/analysis_history/{user_id}_{analysis_id}.json"
        with open(save_path, "w") as f:
            json.dump(error_result, f, indent=2)

@router.get("/{analysis_id}")
async def get_analysis_results(
    analysis_id: str,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get results of a specific RFM analysis.
    """
    try:
        # Check if analysis exists and belongs to user
        db_analysis = db.query(Analysis).filter(
            Analysis.analysis_id == analysis_id,
            Analysis.user_id == user['user_id']
        ).first()
        
        if not db_analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Check if analysis file exists
        file_path = f"storage/analysis_history/{user['user_id']}_{analysis_id}.json"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        # Read analysis results
        with open(file_path, "r") as f:
            result = json.load(f)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

@router.get("/history")
async def get_analysis_history(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get history of all RFM analyses for the current user.
    """
    try:
        # Get analyses from database
        db_analyses = db.query(Analysis).filter(
            Analysis.user_id == user["user_id"]
        ).order_by(Analysis.date_created.desc()).all()
        
        history = []
        
        for analysis in db_analyses:
            history.append({
                "analysis_id": analysis.analysis_id,
                "date_created": analysis.date_created.isoformat(),
                "file_name": analysis.file_name,
                "total_customers": analysis.total_customers,
                "has_error": analysis.has_error
            })
        
        return {"history": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis history: {str(e)}")

@router.post("/{analysis_id}/regenerate-insights")
async def regenerate_insights(
    analysis_id: str,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate AI insights for an existing analysis.
    """
    try:
        # Check if analysis exists and belongs to user
        db_analysis = db.query(Analysis).filter(
            Analysis.analysis_id == analysis_id,
            Analysis.user_id == user['user_id']
        ).first()
        
        if not db_analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Check if analysis file exists
        file_path = f"storage/analysis_history/{user['user_id']}_{analysis_id}.json"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        # Read existing analysis
        with open(file_path, "r") as f:
            analysis = json.load(f)
        
        if "summary" not in analysis:
            raise HTTPException(status_code=400, detail="Analysis does not contain summary data")
        
        # Generate new insights
        insights = await OpenAIService.generate_rfm_insights(analysis["summary"])
        
        # Update insights
        analysis["insights"] = insights
        
        # Save updated analysis
        with open(file_path, "w") as f:
            json.dump(analysis, f, indent=2)
        
        return {"message": "Insights regenerated successfully", "insights": insights}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating insights: {str(e)}")

@router.post("/churn-prediction")
async def predict_churn(
    churn_data: Dict = Body(...),
    user: Dict = Depends(get_current_user)
):
    """
    Generate churn prediction insights based on provided data.
    """
    try:
        # Generate churn insights using OpenAI
        insights = await OpenAIService.generate_churn_insights(churn_data)
        
        return {"insights": insights}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating churn insights: {str(e)}")

@router.post("/ltv-optimization")
async def optimize_ltv(
    ltv_data: Dict = Body(...),
    user: Dict = Depends(get_current_user)
):
    """
    Generate LTV optimization insights based on provided data.
    """
    try:
        # Generate LTV insights using OpenAI
        insights = await OpenAIService.generate_ltv_insights(ltv_data)
        
        return {"insights": insights}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating LTV insights: {str(e)}")

@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an analysis and its associated data.
    """
    try:
        # Check if analysis exists and belongs to user
        db_analysis = db.query(Analysis).filter(
            Analysis.analysis_id == analysis_id,
            Analysis.user_id == user['user_id']
        ).first()
        
        if not db_analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Delete segments from database
        db.query(CustomerSegment).filter(
            CustomerSegment.analysis_id == analysis_id
        ).delete()
        
        # Delete analysis from database
        db.delete(db_analysis)
        db.commit()
        
        # Delete analysis file if it exists
        file_path = f"storage/analysis_history/{user['user_id']}_{analysis_id}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {"message": "Analysis deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting analysis: {str(e)}") 
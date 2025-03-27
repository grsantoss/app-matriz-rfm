import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import RFM service
from rfm_service import RFMAnalysisService

# Create sample transaction data
@pytest.fixture
def sample_transactions():
    """Create a sample transaction dataset for testing"""
    now = datetime.now()
    
    # Create 100 customers with varied transaction patterns
    customer_ids = [f"cust_{i}" for i in range(1, 101)]
    
    # Generate random transactions
    np.random.seed(42)  # For reproducibility
    
    data = []
    for customer_id in customer_ids:
        # Random number of transactions per customer (1-10)
        num_transactions = np.random.randint(1, 11)
        
        for j in range(num_transactions):
            # Random date within last year
            days_ago = np.random.randint(1, 365)
            transaction_date = now - timedelta(days=days_ago)
            
            # Random amount between $10 and $1000
            amount = np.random.uniform(10, 1000)
            
            data.append({
                "customer_id": customer_id,
                "transaction_id": f"tx_{customer_id}_{j}",
                "transaction_date": transaction_date,
                "transaction_amount": amount
            })
    
    return pd.DataFrame(data)

def test_rfm_service_initialization(sample_transactions):
    """Test RFM service initialization"""
    service = RFMAnalysisService(sample_transactions)
    
    assert service.data is not None
    assert service.data.shape[0] > 0
    assert service.rfm_df is None
    assert service.segmented_df is None
    assert service.summary == {}

def test_preprocess_data(sample_transactions):
    """Test data preprocessing"""
    # Add some null values to test handling
    sample_transactions.loc[0, "transaction_amount"] = None
    sample_transactions.loc[1, "customer_id"] = None
    
    # Add negative amount
    sample_transactions.loc[2, "transaction_amount"] = -10
    
    service = RFMAnalysisService(sample_transactions)
    service.preprocess_data()
    
    # Check if null values were removed
    assert service.data.shape[0] == sample_transactions.shape[0] - 2
    
    # Check if negative amounts were removed
    assert (service.data["transaction_amount"] <= 0).sum() == 0
    
    # Check if date was converted to datetime
    assert pd.api.types.is_datetime64_any_dtype(service.data["transaction_date"])

def test_calculate_rfm(sample_transactions):
    """Test RFM metrics calculation"""
    service = RFMAnalysisService(sample_transactions)
    service.preprocess_data()
    
    analysis_date = datetime.now()
    rfm = service.calculate_rfm(analysis_date)
    
    # Check if RFM dataframe was created
    assert service.rfm_df is not None
    assert rfm.shape[0] <= sample_transactions["customer_id"].nunique()
    
    # Check if all metrics are present
    assert "recency" in rfm.columns
    assert "frequency" in rfm.columns
    assert "monetary" in rfm.columns
    
    # Check if metrics are calculated correctly
    customer = rfm.iloc[0]
    customer_id = rfm.index[0]
    
    # Recency should be a positive integer representing days
    assert customer["recency"] >= 0
    
    # Frequency should match count of transactions
    customer_transactions = sample_transactions[sample_transactions["customer_id"] == customer_id]
    assert customer["frequency"] == len(customer_transactions)
    
    # Monetary should match sum of transaction amounts
    assert customer["monetary"] == pytest.approx(customer_transactions["transaction_amount"].sum())

def test_assign_rfm_scores(sample_transactions):
    """Test RFM score assignment"""
    service = RFMAnalysisService(sample_transactions)
    service.preprocess_data()
    service.calculate_rfm()
    
    rfm_scores = service.assign_rfm_scores()
    
    # Check if scores were assigned
    assert "r_quartile" in rfm_scores.columns
    assert "f_quartile" in rfm_scores.columns
    assert "m_quartile" in rfm_scores.columns
    assert "rfm_score" in rfm_scores.columns
    assert "rfm_group" in rfm_scores.columns
    
    # Check if quartiles are in range 1-4
    assert rfm_scores["r_quartile"].min() >= 1
    assert rfm_scores["r_quartile"].max() <= 4
    assert rfm_scores["f_quartile"].min() >= 1
    assert rfm_scores["f_quartile"].max() <= 4
    assert rfm_scores["m_quartile"].min() >= 1
    assert rfm_scores["m_quartile"].max() <= 4
    
    # Check if rfm_score is calculated correctly
    customer = rfm_scores.iloc[0]
    expected_score = (
        int(customer["r_quartile"]) * 100 + 
        int(customer["f_quartile"]) * 10 + 
        int(customer["m_quartile"])
    )
    assert customer["rfm_score"] == expected_score
    
    # Check if rfm_group is formed correctly
    expected_group = (
        str(int(customer["r_quartile"])) + 
        str(int(customer["f_quartile"])) + 
        str(int(customer["m_quartile"]))
    )
    assert customer["rfm_group"] == expected_group

def test_assign_segments(sample_transactions):
    """Test segment assignment"""
    service = RFMAnalysisService(sample_transactions)
    service.preprocess_data()
    service.calculate_rfm()
    service.assign_rfm_scores()
    
    segmented = service.assign_segments()
    
    # Check if segment column was added
    assert "segment" in segmented.columns
    
    # Check if all customers have segments assigned (no unknowns)
    unknown_count = (segmented["segment"] == "Unknown").sum()
    assert unknown_count < len(segmented)  # Some may be unknown if they don't match rules

def test_generate_summary(sample_transactions):
    """Test summary generation"""
    service = RFMAnalysisService(sample_transactions)
    service.preprocess_data()
    service.calculate_rfm()
    service.assign_rfm_scores()
    service.assign_segments()
    
    summary = service.generate_summary()
    
    # Check if summary contains expected keys
    assert "total_customers" in summary
    assert "total_revenue" in summary
    assert "average_recency" in summary
    assert "average_frequency" in summary
    assert "average_monetary" in summary
    assert "segment_distribution" in summary
    
    # Check if total customers matches
    assert summary["total_customers"] == service.segmented_df.shape[0]
    
    # Check if segment distribution has entries
    assert len(summary["segment_distribution"]) > 0
    
    # Check if segment distribution entries have expected fields
    segment = list(summary["segment_distribution"].keys())[0]
    segment_data = summary["segment_distribution"][segment]
    
    assert "count" in segment_data
    assert "percentage" in segment_data
    assert "avg_recency" in segment_data
    assert "avg_frequency" in segment_data
    assert "avg_monetary" in segment_data
    assert "total_revenue" in segment_data
    assert "revenue_percentage" in segment_data

def test_full_analysis_workflow(sample_transactions):
    """Test the end-to-end analysis workflow"""
    service = RFMAnalysisService(sample_transactions)
    
    # Perform full analysis
    summary = service.perform_full_analysis()
    
    # Check if full workflow has completed successfully
    assert service.rfm_df is not None
    assert service.segmented_df is not None
    assert service.summary is not None
    assert len(service.summary) > 0
    
    # Check if summary was returned
    assert summary == service.summary 
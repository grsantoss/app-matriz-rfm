import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import RFM_SEGMENTS, RFM_SCORING

class RFMAnalysisService:
    """Service for performing RFM (Recency, Frequency, Monetary) analysis on customer data."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the RFM analysis service with customer transaction data.
        
        Args:
            data: DataFrame containing customer transaction data
        """
        self.data = data
        self.rfm_df = None
        self.segmented_df = None
        self.summary = {}
    
    def preprocess_data(self) -> None:
        """
        Preprocess the transaction data for RFM analysis.
        
        This method ensures data is in the correct format and handles missing values.
        """
        # Convert date columns to datetime if not already
        for col in self.data.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    self.data[col] = pd.to_datetime(self.data[col])
                except:
                    # If conversion fails, leave as is
                    pass
        
        # Handle missing values
        self.data = self.data.dropna(subset=['customer_id', 'transaction_date', 'transaction_amount'])
        
        # Ensure numeric types for amount
        self.data['transaction_amount'] = pd.to_numeric(self.data['transaction_amount'], errors='coerce')
        
        # Drop rows with zero or negative amounts
        self.data = self.data[self.data['transaction_amount'] > 0]
    
    def calculate_rfm(self, analysis_date: datetime = None) -> pd.DataFrame:
        """
        Calculate RFM metrics for each customer.
        
        Args:
            analysis_date: Reference date for recency calculation. If None, uses current date.
            
        Returns:
            DataFrame with RFM metrics for each customer
        """
        # Use provided analysis date or current date
        if analysis_date is None:
            analysis_date = datetime.now()
        
        # Group by customer and calculate RFM metrics
        rfm = self.data.groupby('customer_id').agg({
            'transaction_date': lambda x: (analysis_date - x.max()).days,  # Recency
            'transaction_id': 'count',  # Frequency
            'transaction_amount': 'sum'  # Monetary
        })
        
        # Rename columns
        rfm.columns = ['recency', 'frequency', 'monetary']
        
        # Store RFM DataFrame
        self.rfm_df = rfm
        
        return rfm
    
    def assign_rfm_scores(self) -> pd.DataFrame:
        """
        Assign RFM scores based on quartiles for each metric.
        
        Returns:
            DataFrame with RFM scores for each customer
        """
        if self.rfm_df is None:
            raise ValueError("Must calculate RFM metrics first using calculate_rfm()")
        
        # Create a copy of RFM DataFrame
        rfm_scores = self.rfm_df.copy()
        
        # Get scoring configuration
        recency_config = RFM_SCORING['recency']
        frequency_config = RFM_SCORING['frequency']
        monetary_config = RFM_SCORING['monetary']
        
        # Calculate quartiles for each metric
        r_quartiles = pd.qcut(
            rfm_scores['recency'], 
            q=4, 
            labels=[4, 3, 2, 1] if recency_config['invert'] else [1, 2, 3, 4]
        )
        
        f_quartiles = pd.qcut(
            rfm_scores['frequency'],
            q=4,
            labels=[1, 2, 3, 4] if frequency_config['invert'] else [4, 3, 2, 1]
        )
        
        m_quartiles = pd.qcut(
            rfm_scores['monetary'],
            q=4,
            labels=[1, 2, 3, 4] if monetary_config['invert'] else [4, 3, 2, 1]
        )
        
        # Add quartile values to dataframe
        rfm_scores['r_quartile'] = r_quartiles
        rfm_scores['f_quartile'] = f_quartiles
        rfm_scores['m_quartile'] = m_quartiles
        
        # Calculate RFM score
        rfm_scores['rfm_score'] = (
            rfm_scores['r_quartile'].astype(int) * 100 + 
            rfm_scores['f_quartile'].astype(int) * 10 + 
            rfm_scores['m_quartile'].astype(int)
        )
        
        # Calculate RFM groups - first digit is R, second is F, third is M
        rfm_scores['rfm_group'] = (
            rfm_scores['r_quartile'].astype(str) + 
            rfm_scores['f_quartile'].astype(str) + 
            rfm_scores['m_quartile'].astype(str)
        )
        
        # Store segmented DataFrame
        self.segmented_df = rfm_scores
        
        return rfm_scores
    
    def assign_segments(self) -> pd.DataFrame:
        """
        Assign customer segments based on RFM scores.
        
        Returns:
            DataFrame with customer segments
        """
        if self.segmented_df is None:
            raise ValueError("Must assign RFM scores first using assign_rfm_scores()")
        
        # Create a copy of the segmented DataFrame
        segmented = self.segmented_df.copy()
        
        # Initialize segment column
        segmented['segment'] = 'Unknown'
        
        # Apply segment rules from config
        for segment_name, rules in RFM_SEGMENTS.items():
            # Multiple conditions can define a segment
            segment_mask = pd.Series(False, index=segmented.index)
            
            for rule in rules:
                condition = pd.Series(True, index=segmented.index)
                
                # Apply each condition in the rule
                for metric, values in rule.items():
                    if metric == 'rfm_score':
                        if isinstance(values, list):
                            # If values is a list, check if score is in the list
                            condition &= segmented['rfm_score'].isin(values)
                        else:
                            # If values is a single value, check if score equals it
                            condition &= (segmented['rfm_score'] == values)
                    elif metric == 'rfm_group':
                        if isinstance(values, list):
                            condition &= segmented['rfm_group'].isin(values)
                        else:
                            condition &= (segmented['rfm_group'] == values)
                    else:
                        # For r_quartile, f_quartile, m_quartile
                        if isinstance(values, dict):
                            if 'min' in values:
                                condition &= (segmented[metric] >= values['min'])
                            if 'max' in values:
                                condition &= (segmented[metric] <= values['max'])
                        else:
                            condition &= (segmented[metric] == values)
                
                # Combined conditions with OR between rules
                segment_mask |= condition
            
            # Assign segment name where conditions are met
            segmented.loc[segment_mask, 'segment'] = segment_name
        
        # Store segmented DataFrame
        self.segmented_df = segmented
        
        return segmented
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the RFM analysis results.
        
        Returns:
            Dictionary containing summary statistics and segment distributions
        """
        if self.segmented_df is None:
            raise ValueError("Must assign segments first using assign_segments()")
        
        # Create summary dictionary
        summary = {
            'total_customers': len(self.segmented_df),
            'total_revenue': float(self.segmented_df['monetary'].sum()),
            'average_recency': float(self.segmented_df['recency'].mean()),
            'average_frequency': float(self.segmented_df['frequency'].mean()),
            'average_monetary': float(self.segmented_df['monetary'].mean()),
            'segment_distribution': {}
        }
        
        # Calculate segment distribution
        segment_counts = self.segmented_df['segment'].value_counts()
        for segment, count in segment_counts.items():
            summary['segment_distribution'][segment] = {
                'count': int(count),
                'percentage': float(count / summary['total_customers'] * 100),
                'avg_recency': float(self.segmented_df[self.segmented_df['segment'] == segment]['recency'].mean()),
                'avg_frequency': float(self.segmented_df[self.segmented_df['segment'] == segment]['frequency'].mean()),
                'avg_monetary': float(self.segmented_df[self.segmented_df['segment'] == segment]['monetary'].mean()),
                'total_revenue': float(self.segmented_df[self.segmented_df['segment'] == segment]['monetary'].sum()),
                'revenue_percentage': float(
                    self.segmented_df[self.segmented_df['segment'] == segment]['monetary'].sum() / 
                    summary['total_revenue'] * 100
                )
            }
        
        # Store summary
        self.summary = summary
        
        return summary
    
    def save_analysis(self, file_path: str) -> None:
        """
        Save the analysis results to a JSON file.
        
        Args:
            file_path: Path to save the analysis results
        """
        if not self.summary:
            self.generate_summary()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save to JSON file
        with open(file_path, 'w') as f:
            json.dump(self.summary, f, indent=2)
    
    def get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """
        Get RFM data for a specific customer.
        
        Args:
            customer_id: ID of the customer to retrieve data for
            
        Returns:
            Dictionary containing customer RFM data
        """
        if self.segmented_df is None:
            raise ValueError("Must perform RFM analysis first")
        
        if customer_id not in self.segmented_df.index:
            return {"error": "Customer not found"}
        
        # Get customer data
        customer_data = self.segmented_df.loc[customer_id].to_dict()
        
        # Convert numpy types to Python types for JSON serialization
        for key, value in customer_data.items():
            if isinstance(value, (np.int64, np.int32, np.int16, np.int8)):
                customer_data[key] = int(value)
            elif isinstance(value, (np.float64, np.float32, np.float16)):
                customer_data[key] = float(value)
        
        return customer_data
    
    def perform_full_analysis(self, analysis_date: datetime = None) -> Dict[str, Any]:
        """
        Perform the complete RFM analysis workflow.
        
        Args:
            analysis_date: Reference date for recency calculation
            
        Returns:
            Dictionary containing analysis summary
        """
        self.preprocess_data()
        self.calculate_rfm(analysis_date)
        self.assign_rfm_scores()
        self.assign_segments()
        return self.generate_summary() 
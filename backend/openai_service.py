import openai
import json
import sys
import os
from typing import Dict, Any, List

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import OPENAI_API_KEY, OPENAI_MODEL, AI_PROMPTS

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

class OpenAIService:
    """Service for generating insights using OpenAI GPT models."""
    
    @staticmethod
    async def generate_rfm_insights(analysis_summary: Dict[str, Any]) -> str:
        """
        Generate marketing insights for RFM analysis results.
        
        Args:
            analysis_summary: Summary of RFM analysis results
            
        Returns:
            Generated insights as string
        """
        try:
            # Format analysis summary as string
            analysis_text = json.dumps(analysis_summary, indent=2)
            
            # Replace placeholder in prompt
            prompt = AI_PROMPTS["rfm_insights"].format(analysis_summary=analysis_text)
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a marketing and RFM analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract and return the generated text
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating RFM insights: {e}")
            return "Não foi possível gerar insights. Por favor, tente novamente mais tarde."
    
    @staticmethod
    async def generate_churn_insights(churn_data: Dict[str, Any]) -> str:
        """
        Generate insights for churn prediction data.
        
        Args:
            churn_data: Churn prediction data
            
        Returns:
            Generated insights as string
        """
        try:
            # Format churn data as string
            churn_text = json.dumps(churn_data, indent=2)
            
            # Replace placeholder in prompt
            prompt = AI_PROMPTS["churn_prediction"].format(churn_data=churn_text)
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a customer retention and churn prevention expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Extract and return the generated text
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating churn insights: {e}")
            return "Não foi possível gerar insights de churn. Por favor, tente novamente mais tarde."
    
    @staticmethod
    async def generate_ltv_insights(ltv_data: Dict[str, Any]) -> str:
        """
        Generate insights for LTV optimization.
        
        Args:
            ltv_data: Lifetime Value data
            
        Returns:
            Generated insights as string
        """
        try:
            # Format LTV data as string
            ltv_text = json.dumps(ltv_data, indent=2)
            
            # Replace placeholder in prompt
            prompt = AI_PROMPTS["ltv_optimization"].format(ltv_data=ltv_text)
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a customer lifetime value optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Extract and return the generated text
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating LTV insights: {e}")
            return "Não foi possível gerar insights de LTV. Por favor, tente novamente mais tarde." 
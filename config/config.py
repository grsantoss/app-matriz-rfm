# RFM Matrix Configuration File

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Configuration
PROJECT_NAME = os.getenv("PROJECT_NAME", "Matriz RFM")
ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Domain Configuration
FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN", "app.matrizrfm.com.br")
BACKEND_DOMAIN = os.getenv("BACKEND_DOMAIN", "api.matrizrfm.com.br")
PGADMIN_DOMAIN = os.getenv("PGADMIN_DOMAIN", "pgadmin.matrizrfm.com.br")
PORTAINER_DOMAIN = os.getenv("PORTAINER_DOMAIN", "painel.matrizrfm.com.br")

# URLs
FRONTEND_URL = f"https://{FRONTEND_DOMAIN}"
BACKEND_URL = f"https://{BACKEND_DOMAIN}"
PGADMIN_URL = f"https://{PGADMIN_DOMAIN}"
PORTAINER_URL = f"https://{PORTAINER_DOMAIN}"

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "matriz_rfm")
}
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# JWT Configuration
JWT_CONFIG = {
    "secret": os.getenv("JWT_SECRET"),
    "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
    "expiration": os.getenv("JWT_EXPIRATION", "24h")
}

# Email Configuration (Amazon SES)
EMAIL_CONFIG = {
    "host": os.getenv("SMTP_HOST", "email-smtp.us-east-1.amazonaws.com"),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("SMTP_USERNAME"),
    "password": os.getenv("SMTP_PASSWORD")
}

# OpenAI Configuration
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": os.getenv("OPENAI_MODEL", "gpt-4")
}

# Auth Service Configuration
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", f"{BACKEND_URL}/auth")

# RFM Analysis Rules
RFM_RULES = {
    "segments": {
        "champions": {
            "r": {"min": 4, "max": 5},
            "f": {"min": 4, "max": 5},
            "m": {"min": 4, "max": 5}
        },
        "loyal_customers": {
            "r": {"min": 3, "max": 5},
            "f": {"min": 3, "max": 5},
            "m": {"min": 3, "max": 5}
        },
        "at_risk": {
            "r": {"min": 1, "max": 2},
            "f": {"min": 3, "max": 5},
            "m": {"min": 3, "max": 5}
        },
        "lost": {
            "r": {"min": 1, "max": 2},
            "f": {"min": 1, "max": 2},
            "m": {"min": 1, "max": 2}
        }
    },
    "scoring": {
        "recency": {
            "invert": True,
            "quartiles": {
                "q1": 5, "q2": 4, "q3": 3, "q4": 2, "q5": 1
            }
        },
        "frequency": {
            "invert": False,
            "quartiles": {
                "q1": 1, "q2": 2, "q3": 3, "q4": 4, "q5": 5
            }
        },
        "monetary": {
            "invert": False,
            "quartiles": {
                "q1": 1, "q2": 2, "q3": 3, "q4": 4, "q5": 5
            }
        }
    }
}

# OpenAI Prompts
OPENAI_PROMPTS = {
    "rfm_insights": "Generate strategic insights based on RFM analysis data",
    "churn_insights": "Generate strategic insights based on churn prediction data",
    "ltv_insights": "Generate strategic insights based on LTV optimization data"
}

# Amazon SES Configuration for Email
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "noreply@matrizrfm.com")

# Message Generation Configuration
MESSAGE_LIMITS = {
    "sms": 160,
    "whatsapp": 500,
    "email": 800
}

MAX_REGENERATION_ATTEMPTS = 3
MAX_MESSAGES_PER_GENERATION = 5
MESSAGE_HISTORY_DAYS = 7

# Message Generation Prompts
PROMPT_TEMPLATES = {
    "sms": "Gere uma mensagem SMS promocional em português do Brasil, limitada a {limit} caracteres, para {segment} com objetivo de {objective}. Tom: {tone}. Empresa: {company}.",
    "whatsapp": "Crie uma mensagem WhatsApp promocional em português do Brasil, limitada a {limit} caracteres, incluindo emojis adequados, para {segment} com objetivo de {objective}. Tom: {tone}. Empresa: {company}.",
    "email": "Elabore um email promocional em português do Brasil, limitado a {limit} caracteres, com estrutura clara (saudação, corpo e chamada para ação), para {segment} com objetivo de {objective}. Tom: {tone}. Empresa: {company}."
}

# AI Insights Configuration
AI_INSIGHTS_MAX_LENGTH = 1500
AI_INSIGHTS_TEMPERATURE = 0.7

# AI Insights Prompts
AI_INSIGHTS_PROMPTS = {
    "general": "Analise os dados da matriz RFM apresentada e gere insights estratégicos de marketing em português do Brasil. Forneça recomendações específicas e acionáveis para melhorar o engajamento e aumentar o valor do cliente. Foque em estratégias personalizadas para cada segmento RFM identificado.",
    "segment_specific": "Com base na análise RFM, gere insights estratégicos em português do Brasil para o segmento '{segment}'. Forneça 3-5 recomendações específicas e acionáveis que possam ser implementadas para melhorar o engajamento, retenção e valor deste segmento de clientes.",
    "business_specific": "Considerando o tipo de negócio '{business_type}' e os dados da análise RFM, gere insights estratégicos de marketing em português do Brasil. Forneça recomendações específicas para este setor, focando em como melhorar a retenção de clientes, aumentar o valor médio de compra e reativar clientes dormentes."
}

# Password Reset Configuration
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 24
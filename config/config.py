# RFM Matrix Configuration File

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# General Configuration
PROJECT_NAME = "Matriz RFM"
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"

# Domain Settings
FRONTEND_DOMAIN = os.getenv("FRONTEND_DOMAIN", "app.matrizrfm.com.br")
BACKEND_DOMAIN = os.getenv("BACKEND_DOMAIN", "api.matrizrfm.com.br")
PGADMIN_DOMAIN = os.getenv("PGADMIN_DOMAIN", "pgadmin.matrizrfm.com.br")

# URLs
FRONTEND_URL = f"http://{FRONTEND_DOMAIN}"
BACKEND_URL = f"http://{BACKEND_DOMAIN}"

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", 5432),
    "user": os.getenv("DB_USER", "rfmuser"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "rfmmatrix"),
}
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Email Configuration (Amazon SES)
EMAIL_CONFIG = {
    "host": os.getenv("SMTP_HOST", "email-smtp.us-east-1.amazonaws.com"),
    "port": os.getenv("SMTP_PORT", 587),
    "user": os.getenv("SMTP_USER", ""),
    "password": os.getenv("SMTP_PASS", ""),
    "from_email": os.getenv("EMAIL_FROM", "no-reply@matrizrfm.com.br"),
}

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4-turbo"

# RFM Analysis Rules
RFM_RULES = {
    "segments": {
        "champions": {
            "min_recency": 4,
            "min_frequency": 4,
            "min_monetary": 4,
            "description": "Clientes que compraram recentemente, compram com frequência e gastam muito. Eles são seus melhores clientes."
        },
        "loyal_customers": {
            "min_recency": 3,
            "min_frequency": 3,
            "min_monetary": 3,
            "description": "Clientes que compram regularmente. Respondem bem a programas de fidelidade."
        },
        "potential_loyalists": {
            "min_recency": 4,
            "min_frequency": 2,
            "min_monetary": 2,
            "max_frequency": 3,
            "max_monetary": 3,
            "description": "Clientes recentes que gastam um bom valor. Podem ser convertidos em clientes fiéis com atenção adequada."
        },
        "new_customers": {
            "min_recency": 4,
            "max_frequency": 1,
            "description": "Clientes que compraram recentemente, mas não compraram com frequência."
        },
        "promising": {
            "min_recency": 3,
            "max_frequency": 2,
            "min_monetary": 3,
            "description": "Clientes recentes que gastam um bom valor, mas não compram com frequência."
        },
        "needing_attention": {
            "min_recency": 2,
            "max_recency": 3,
            "min_frequency": 2,
            "max_frequency": 3,
            "min_monetary": 2,
            "max_monetary": 3,
            "description": "Clientes médios em termos de recência, frequência e valor monetário."
        },
        "about_to_sleep": {
            "max_recency": 2,
            "min_frequency": 2,
            "max_frequency": 3,
            "min_monetary": 2,
            "max_monetary": 3,
            "description": "Clientes que não compram há algum tempo, mas têm frequência e valor médios."
        },
        "cant_lose": {
            "max_recency": 2,
            "min_frequency": 3,
            "min_monetary": 3,
            "description": "Clientes que não compram há algum tempo, mas têm alta frequência e valor."
        },
        "at_risk": {
            "max_recency": 2,
            "min_frequency": 2,
            "max_frequency": 3,
            "description": "Clientes que não compram há algum tempo e têm frequência média."
        },
        "hibernating": {
            "max_recency": 1,
            "max_frequency": 2,
            "max_monetary": 2,
            "description": "Clientes que não compram há muito tempo, têm baixa frequência e baixo valor."
        },
        "lost": {
            "max_recency": 1,
            "max_frequency": 1,
            "description": "Clientes que não compram há muito tempo e têm baixa frequência."
        }
    },
    "score_mapping": {
        "recency": {
            "invert": True,  # Lower recency days -> higher score
            "quartiles": 4
        },
        "frequency": {
            "invert": False,  # Higher frequency -> higher score
            "quartiles": 4
        },
        "monetary": {
            "invert": False,  # Higher monetary -> higher score
            "quartiles": 4
        }
    }
}

# OpenAI Prompts
AI_PROMPTS = {
    "rfm_insights": """
    Você é um especialista em análise RFM (Recência, Frequência, Monetário) e marketing.
    
    Baseado na seguinte análise RFM:
    
    {analysis_summary}
    
    Forneça insights estratégicos e recomendações de marketing específicas para cada segmento de clientes.
    
    Organize sua resposta da seguinte forma:
    1. Uma visão geral da situação atual da empresa com base na análise RFM
    2. Insights importantes sobre os principais segmentos de clientes
    3. Recomendações de marketing e ações específicas para cada segmento
    4. Priorização de esforços (quais segmentos devem receber mais atenção)
    5. Métricas a serem monitoradas para avaliar o sucesso das ações
    
    Seja específico, prático e estratégico em suas recomendações.
    """,
    
    "churn_prediction": """
    Você é um especialista em prevenção de churn (abandono de clientes).
    
    Com base nos seguintes dados de previsão de churn:
    
    {churn_data}
    
    Forneça insights e recomendações para:
    1. Identificar os padrões principais que levam ao churn
    2. Estratégias específicas para reduzir o churn em cada segmento de risco
    3. Abordagens proativas para reter clientes de alto valor
    
    Inclua exemplos de ações específicas e campanhas personalizadas.
    """,
    
    "ltv_optimization": """
    Você é um especialista em Lifetime Value (LTV) de clientes.
    
    Com base na seguinte análise de LTV:
    
    {ltv_data}
    
    Forneça insights e estratégias para:
    1. Aumentar o LTV dos diferentes segmentos de clientes
    2. Identificar oportunidades de cross-selling e upselling
    3. Estratégias de retenção específicas para maximizar o valor no longo prazo
    
    Inclua exemplos de empresas que implementaram estratégias semelhantes com sucesso.
    """
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
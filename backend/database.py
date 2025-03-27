import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DB_CONFIG

# Create SQLAlchemy engine and session
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db']}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    analyses = relationship("Analysis", back_populates="user")
    
class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID as string
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    total_customers = Column(Integer, nullable=True)
    has_error = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="analyses")
    
class CustomerSegment(Base):
    __tablename__ = "customer_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(36), ForeignKey("analyses.analysis_id"), nullable=False)
    segment_name = Column(String(255), nullable=False)
    customer_count = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    avg_recency = Column(Float, nullable=True)
    avg_frequency = Column(Float, nullable=True)
    avg_monetary = Column(Float, nullable=True)
    total_revenue = Column(Float, nullable=True)
    revenue_percentage = Column(Float, nullable=True)
    
    analysis = relationship("Analysis")
    
# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created.") 
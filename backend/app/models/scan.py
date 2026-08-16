from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Numeric
from sqlalchemy.sql import func
from app.db.database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    contract_name = Column(String(255), nullable=True)
    contract_code = Column(Text, nullable=False)
    risk_score = Column(Numeric(4, 1))
    risk_level = Column(String(20))
    findings_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
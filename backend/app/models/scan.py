from sqlalchemy import Column, Integer, Text, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)

    contract_code = Column(
        Text,
        nullable=False,
    )

    contract_name = Column(
        String(255),
        nullable=True,
    )

    total_findings = Column(
        Integer,
        default=0,
    )

    overall_risk = Column(
        Numeric(4, 1),
        nullable=True,
    )

    findings_json = Column(
        JSONB,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
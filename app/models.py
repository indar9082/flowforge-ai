from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from app.database import Base

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False, default="completed")
    rows_in = Column(Integer, nullable=False, default=0)
    rows_out = Column(Integer, nullable=False, default=0)
    columns_out = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Float, nullable=False, default=0)
    transformations = Column(Text, nullable=False, default="[]")
    quality_report = Column(Text, nullable=False, default="{}")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

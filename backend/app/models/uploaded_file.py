from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # csv, excel
    original_rows = Column(Integer)
    transformed_rows = Column(Integer)
    columns = Column(JSON)  # Guardar lista de columnas
    created_at = Column(DateTime, default=datetime.utcnow)
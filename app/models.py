from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    text = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from config.db import Base

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    content = Column(JSONB)  # store requirement content as JSON
    confluence_page_id = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Epic(Base):
    __tablename__ = "epics"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"))
    name = Column(String(255))
    content = Column(JSONB)  # epic details as JSON
    confluence_page_id = Column(String(255), nullable=True)  # Confluence page ID
    created_at = Column(TIMESTAMP, server_default=func.now())

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, index=True)
    epic_id = Column(Integer, ForeignKey("epics.id", ondelete="CASCADE"))
    name = Column(String(255))
    content = Column(JSONB)  # story details as JSON
    created_at = Column(TIMESTAMP, server_default=func.now())

class QA(Base):
    __tablename__ = "qa"
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=True)
    epic_id = Column(Integer, ForeignKey("epics.id", ondelete="CASCADE"), nullable=True)
    type = Column(String(50))  # test_plan, api_test, automation_script
    content = Column(JSONB)
    confluence_page_id = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class AggregatedUpload(Base):
    __tablename__ = "aggregated_uploads"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"))
    content = Column(JSONB)  # full hierarchy as JSON
    created_at = Column(TIMESTAMP, server_default=func.now())

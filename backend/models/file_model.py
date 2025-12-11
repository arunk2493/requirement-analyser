from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    # Jira credentials (encrypted in production recommended)
    jira_url = Column(String(512), nullable=True)
    jira_username = Column(String(255), nullable=True)
    jira_api_token = Column(String(512), nullable=True)
    jira_project_key = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255))
    content = Column(JSONB)  # store requirement content as JSON
    confluence_page_id = Column(String(50), nullable=True)
    vectorstore_id = Column(String(255), nullable=True)  # unique ID for this upload's vector store
    created_at = Column(TIMESTAMP, server_default=func.now())

class Epic(Base):
    __tablename__ = "epics"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"))
    name = Column(String(255))
    content = Column(JSONB)  # epic details as JSON
    confluence_page_id = Column(String(255), nullable=True)  # Confluence page ID
    jira_key = Column(String(50), nullable=True)  # Jira issue key (e.g., PROJ-1)
    jira_issue_id = Column(String(50), nullable=True)  # Jira issue ID (numeric, e.g., 10028)
    jira_url = Column(String(512), nullable=True)  # Jira issue URL
    jira_creation_success = Column(Boolean, nullable=True)  # True if Jira creation succeeded, False if failed, None if not attempted
    created_at = Column(TIMESTAMP, server_default=func.now())

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, index=True)
    epic_id = Column(Integer, ForeignKey("epics.id", ondelete="CASCADE"))
    name = Column(String(255))
    content = Column(JSONB)  # story details as JSON
    jira_key = Column(String(50), nullable=True)  # Jira issue key (e.g., PROJ-2)
    jira_issue_id = Column(String(50), nullable=True)  # Jira issue ID (numeric, e.g., 10030)
    jira_url = Column(String(512), nullable=True)  # Jira issue URL
    epic_jira_key = Column(String(50), nullable=True)  # Parent epic's Jira key
    epic_jira_issue_id = Column(String(50), nullable=True)  # Parent epic's Jira issue ID (numeric)
    jira_creation_success = Column(Boolean, nullable=True)  # True if Jira creation succeeded, False if failed, None if not attempted
    created_at = Column(TIMESTAMP, server_default=func.now())

class QA(Base):
    __tablename__ = "qa"
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=True)
    epic_id = Column(Integer, ForeignKey("epics.id", ondelete="CASCADE"), nullable=True)
    type = Column(String(50))  # test_plan, api_test, automation_script
    test_type = Column(String(50), nullable=True)  # functional, non_functional, api
    content = Column(JSONB)
    confluence_page_id = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class AggregatedUpload(Base):
    __tablename__ = "aggregated_uploads"
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id", ondelete="CASCADE"))
    content = Column(JSONB)  # full hierarchy as JSON
    created_at = Column(TIMESTAMP, server_default=func.now())

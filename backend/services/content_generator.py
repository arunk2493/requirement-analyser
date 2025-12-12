"""Unified generation service for all content types (epics, stories, QA, test plans)"""
import logging
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from config.gemini import generate_json
from models.file_model import Epic, Story, QA, Upload
from rag.vectorstore import VectorStore
from utils.json_parser import parse_model_json, ensure_dict_list
from utils.error_handler import ProcessingError, ResourceNotFoundError, ValidationError

logger = logging.getLogger(__name__)


class ContentGenerationService:
    """Service for generating and storing various content types"""
    
    CONTENT_TYPES = {
        "epics": "epic",
        "stories": "story",
        "qa": "qa",
        "test_plan": "test_plan"
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.vectorstore = VectorStore()
    
    def generate_epics(self, upload_id: int, prompt_template: str) -> List[Dict[str, Any]]:
        """
        Generate epics from upload content.
        
        Args:
            upload_id: ID of the upload
            prompt_template: Prompt template with {requirement_text} placeholder
            
        Returns:
            List of generated epic dictionaries
            
        Raises:
            ResourceNotFoundError: If upload not found
            ProcessingError: If generation fails
        """
        # Fetch upload
        upload_obj = self.db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload_obj:
            raise ResourceNotFoundError("Upload", upload_id)
        
        try:
            # Generate from Gemini
            prompt = prompt_template.format(requirement_text=upload_obj.content)
            epics_raw = generate_json(prompt)
            epics_list = ensure_dict_list(epics_raw)
            
            logger.info(f"Generated {len(epics_list)} epics from upload {upload_id}")
            return epics_list
            
        except Exception as e:
            logger.error(f"Failed to generate epics: {str(e)}")
            raise ProcessingError(
                f"Failed to generate epics: {str(e)}",
                operation="generate_epics"
            )
    
    def generate_stories(self, epic_id: int, prompt_template: str) -> List[Dict[str, Any]]:
        """
        Generate stories from epic content.
        
        Args:
            epic_id: ID of the epic
            prompt_template: Prompt template with {epic_content} placeholder
            
        Returns:
            List of generated story dictionaries
            
        Raises:
            ResourceNotFoundError: If epic not found
            ProcessingError: If generation fails
        """
        # Fetch epic
        epic_obj = self.db.query(Epic).filter(Epic.id == epic_id).first()
        if not epic_obj:
            raise ResourceNotFoundError("Epic", epic_id)
        
        try:
            # Generate from Gemini
            prompt = prompt_template.format(epic_content=epic_obj.content)
            stories_raw = generate_json(prompt)
            stories_list = ensure_dict_list(stories_raw)
            
            logger.info(f"Generated {len(stories_list)} stories from epic {epic_id}")
            return stories_list
            
        except Exception as e:
            logger.error(f"Failed to generate stories: {str(e)}")
            raise ProcessingError(
                f"Failed to generate stories: {str(e)}",
                operation="generate_stories"
            )
    
    def generate_qa(self, story_id: int, prompt_template: str) -> List[Dict[str, Any]]:
        """
        Generate QA test cases from story content.
        
        Args:
            story_id: ID of the story
            prompt_template: Prompt template with {story_content} placeholder
            
        Returns:
            List of generated QA test dictionaries
            
        Raises:
            ResourceNotFoundError: If story not found
            ProcessingError: If generation fails
        """
        # Fetch story
        story_obj = self.db.query(Story).filter(Story.id == story_id).first()
        if not story_obj:
            raise ResourceNotFoundError("Story", story_id)
        
        try:
            # Generate from Gemini
            prompt = prompt_template.format(story_content=story_obj.content)
            qa_raw = generate_json(prompt)
            qa_list = ensure_dict_list(qa_raw)
            
            logger.info(f"Generated {len(qa_list)} QA test cases from story {story_id}")
            return qa_list
            
        except Exception as e:
            logger.error(f"Failed to generate QA: {str(e)}")
            raise ProcessingError(
                f"Failed to generate QA: {str(e)}",
                operation="generate_qa"
            )
    
    def generate_test_plan(self, epic_id: int, prompt_template: str) -> List[Dict[str, Any]]:
        """
        Generate test plans from epic content.
        
        Args:
            epic_id: ID of the epic
            prompt_template: Prompt template with {epic_content} placeholder
            
        Returns:
            List of generated test plan dictionaries
            
        Raises:
            ResourceNotFoundError: If epic not found
            ProcessingError: If generation fails
        """
        # Fetch epic
        epic_obj = self.db.query(Epic).filter(Epic.id == epic_id).first()
        if not epic_obj:
            raise ResourceNotFoundError("Epic", epic_id)
        
        try:
            # Generate from Gemini
            prompt = prompt_template.format(epic_content=epic_obj.content)
            testplan_raw = generate_json(prompt)
            testplan_list = ensure_dict_list(testplan_raw)
            
            logger.info(f"Generated {len(testplan_list)} test plans from epic {epic_id}")
            return testplan_list
            
        except Exception as e:
            logger.error(f"Failed to generate test plan: {str(e)}")
            raise ProcessingError(
                f"Failed to generate test plan: {str(e)}",
                operation="generate_test_plan"
            )
    
    def save_epics(self, upload_id: int, epics_data: List[Dict[str, Any]]) -> List[Tuple[int, Dict]]:
        """
        Save generated epics to database and vectorstore.
        
        Args:
            upload_id: ID of the parent upload
            epics_data: List of epic data dictionaries
            
        Returns:
            List of (epic_id, epic_data) tuples
        """
        saved_epics = []
        
        for epic_data in epics_data:
            try:
                epic = Epic(
                    upload_id=upload_id,
                    name=epic_data.get("name", "Unnamed Epic"),
                    content=epic_data
                )
                self.db.add(epic)
                self.db.flush()  # Get generated ID
                
                # Index in vectorstore
                self._index_in_vectorstore(
                    text=f"Epic: {epic.name}\nDescription: {epic_data.get('description', '')}",
                    doc_type="epic",
                    resource_id=epic.id,
                    resource_name=epic.name
                )
                
                saved_epics.append((epic.id, epic_data))
                logger.debug(f"Saved epic {epic.id}: {epic.name}")
                
            except Exception as e:
                logger.error(f"Failed to save epic: {str(e)}")
                continue
        
        self.db.commit()
        return saved_epics
    
    def save_stories(self, epic_id: int, stories_data: List[Dict[str, Any]]) -> List[Tuple[int, Dict]]:
        """
        Save generated stories to database and vectorstore.
        
        Args:
            epic_id: ID of the parent epic
            stories_data: List of story data dictionaries
            
        Returns:
            List of (story_id, story_data) tuples
        """
        saved_stories = []
        
        for story_data in stories_data:
            try:
                story = Story(
                    epic_id=epic_id,
                    name=story_data.get("name", "Unnamed Story"),
                    content=story_data
                )
                self.db.add(story)
                self.db.flush()  # Get generated ID
                
                # Index in vectorstore
                criteria = ", ".join(story_data.get("acceptanceCriteria", []))
                self._index_in_vectorstore(
                    text=f"Story: {story.name}\nDescription: {story_data.get('description', '')}\nCriteria: {criteria}",
                    doc_type="story",
                    resource_id=story.id,
                    resource_name=story.name,
                    parent_id=epic_id
                )
                
                saved_stories.append((story.id, story_data))
                logger.debug(f"Saved story {story.id}: {story.name}")
                
            except Exception as e:
                logger.error(f"Failed to save story: {str(e)}")
                continue
        
        self.db.commit()
        return saved_stories
    
    def save_qa(self, story_id: int, qa_data_list: List[Dict[str, Any]], qa_type: str = "qa") -> List[Tuple[int, Dict]]:
        """
        Save QA test cases to database and vectorstore.
        
        Args:
            story_id: ID of the parent story (can be None for test plans)
            qa_data_list: List of QA data dictionaries
            qa_type: Type of QA (qa, test_plan, etc.)
            
        Returns:
            List of (qa_id, qa_data) tuples
        """
        saved_qa = []
        
        for qa_item in qa_data_list:
            try:
                qa_obj = QA(
                    story_id=story_id,
                    type=qa_type,
                    content=qa_item
                )
                self.db.add(qa_obj)
                self.db.flush()  # Get generated ID
                
                # Index in vectorstore
                title = qa_item.get("title", "Unnamed QA")
                self._index_in_vectorstore(
                    text=f"QA Test: {title}\n{str(qa_item)}",
                    doc_type=qa_type,
                    resource_id=qa_obj.id,
                    resource_name=title,
                    parent_id=story_id
                )
                
                saved_qa.append((qa_obj.id, qa_item))
                logger.debug(f"Saved {qa_type} {qa_obj.id}: {title}")
                
            except Exception as e:
                logger.error(f"Failed to save QA: {str(e)}")
                continue
        
        self.db.commit()
        return saved_qa
    
    def _index_in_vectorstore(self, text: str, doc_type: str, resource_id: int, 
                             resource_name: str, parent_id: Optional[int] = None) -> None:
        """
        Index document in vectorstore for RAG.
        
        Args:
            text: Text content to index
            doc_type: Type of document (epic, story, qa, etc.)
            resource_id: ID of the resource
            resource_name: Name of the resource
            parent_id: Optional parent resource ID
        """
        try:
            doc_id = f"{doc_type}_{resource_id}_{str(uuid.uuid4())[:8]}"
            metadata = {
                "type": doc_type,
                "resource_id": resource_id,
                "resource_name": resource_name
            }
            if parent_id:
                metadata["parent_id"] = parent_id
            
            self.vectorstore.store_document(text, doc_id, metadata=metadata)
            logger.debug(f"Indexed document {doc_id} in vectorstore")
        except Exception as e:
            logger.warning(f"Could not index {doc_type} in vectorstore: {str(e)}")

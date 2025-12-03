from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Standard response format from agents"""
    success: bool
    data: Any
    message: str
    agent_name: str
    timestamp: str
    error: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all agents in the agentic system"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> AgentResponse:
        """Execute the agent with the given context.
        
        Args:
            context: Dictionary with input data for the agent
            
        Returns:
            AgentResponse with results or error
        """
        pass

    def log_execution(self, level: str, message: str):
        """Log agent execution"""
        if level == "info":
            self.logger.info(f"[{self.name}] {message}")
        elif level == "error":
            self.logger.error(f"[{self.name}] {message}")
        elif level == "debug":
            self.logger.debug(f"[{self.name}] {message}")

    def create_response(
        self,
        success: bool,
        data: Any,
        message: str,
        error: Optional[str] = None
    ) -> AgentResponse:
        """Create a standardized response"""
        return AgentResponse(
            success=success,
            data=data,
            message=message,
            agent_name=self.name,
            timestamp=datetime.now().isoformat(),
            error=error
        )

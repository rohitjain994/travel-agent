"""Base agent class for all travel agent components."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY, MODEL_NAME, TEMPERATURE
from logger_config import logger


class BaseAgent(ABC):
    """Base class for all agents in the travel agent system."""
    
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE,
        )
    
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task based on the current state."""
        pass
    
    def _format_prompt(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Format the prompt with system instructions and context."""
        prompt = f"{self.system_prompt}\n\n"
        
        if context:
            prompt += f"Context: {context}\n\n"
        
        prompt += f"User Request: {user_input}\n\n"
        prompt += "Please provide your response:"
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        start_time = time.time()
        
        # Log LLM call start
        logger.log_operation(
            agent=self.name,
            operation="LLM Call Started",
            details=f"Prompt length: {len(prompt)} characters",
            status="info"
        )
        
        try:
            # Combine system prompt and user prompt
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            response = self.llm.invoke(full_prompt)
            
            # Handle different response types
            if hasattr(response, 'content'):
                response_text = response.content
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)
            
            duration = time.time() - start_time
            
            # Log successful LLM call
            logger.log_llm_call(
                agent=self.name,
                prompt_length=len(full_prompt),
                response_length=len(response_text),
                duration=duration
            )
            
            return response_text
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"LLM call failed: {str(e)}"
            logger.log_operation(
                agent=self.name,
                operation="LLM Call Failed",
                details=error_msg,
                status="error",
                duration=duration
            )
            raise


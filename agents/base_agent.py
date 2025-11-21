"""Base agent class for all travel agent components."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import time
import random
from langchain_google_genai import ChatGoogleGenerativeAI
from config import (
    GEMINI_API_KEY, 
    MODEL_NAME, 
    TEMPERATURE,
    MAX_RETRIES,
    INITIAL_RETRY_DELAY,
    MAX_RETRY_DELAY,
    RETRY_BACKOFF_MULTIPLIER
)
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
        """Call the LLM with retry logic and exponential backoff for rate limiting."""
        start_time = time.time()
        
        # Log LLM call start
        logger.log_operation(
            agent=self.name,
            operation="LLM Call Started",
            details=f"Prompt length: {len(prompt)} characters",
            status="info"
        )
        
        # Combine system prompt and user prompt
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        
        last_exception = None
        retry_delay = INITIAL_RETRY_DELAY
        
        for attempt in range(MAX_RETRIES + 1):
            try:
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
                if attempt > 0:
                    logger.log_operation(
                        agent=self.name,
                        operation="LLM Call Succeeded After Retry",
                        details=f"Attempt {attempt + 1} succeeded",
                        status="success",
                        duration=duration
                    )
                else:
                    logger.log_llm_call(
                        agent=self.name,
                        prompt_length=len(full_prompt),
                        response_length=len(response_text),
                        duration=duration
                    )
                
                return response_text
                
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                
                # Check if it's a rate limit error (429)
                is_rate_limit = (
                    "429" in error_str or
                    "resource exhausted" in error_str or
                    "quota exceeded" in error_str or
                    "rate limit" in error_str or
                    "too many requests" in error_str
                )
                
                # Check if it's a retryable error
                is_retryable = (
                    is_rate_limit or
                    "503" in error_str or  # Service unavailable
                    "500" in error_str or  # Internal server error
                    "timeout" in error_str or
                    "deadline exceeded" in error_str
                )
                
                duration = time.time() - start_time
                
                if is_rate_limit:
                    logger.log_operation(
                        agent=self.name,
                        operation="Rate Limit Error (429)",
                        details=f"Attempt {attempt + 1}/{MAX_RETRIES + 1}: {str(e)}",
                        status="warning",
                        duration=duration
                    )
                else:
                    logger.log_operation(
                        agent=self.name,
                        operation="LLM Call Error",
                        details=f"Attempt {attempt + 1}/{MAX_RETRIES + 1}: {str(e)}",
                        status="error" if not is_retryable else "warning",
                        duration=duration
                    )
                
                # If it's the last attempt or not retryable, raise the exception
                if attempt >= MAX_RETRIES or not is_retryable:
                    break
                
                # Calculate exponential backoff with jitter
                delay = min(retry_delay, MAX_RETRY_DELAY)
                jitter = random.uniform(0, delay * 0.1)  # Add 10% jitter
                total_delay = delay + jitter
                
                logger.log_operation(
                    agent=self.name,
                    operation="Retrying LLM Call",
                    details=f"Waiting {total_delay:.2f}s before retry {attempt + 2}/{MAX_RETRIES + 1}",
                    status="info"
                )
                
                time.sleep(total_delay)
                retry_delay *= RETRY_BACKOFF_MULTIPLIER
        
        # If we get here, all retries failed
        duration = time.time() - start_time
        error_msg = f"LLM call failed after {MAX_RETRIES + 1} attempts: {str(last_exception)}"
        
        logger.log_operation(
            agent=self.name,
            operation="LLM Call Failed - All Retries Exhausted",
            details=error_msg,
            status="error",
            duration=duration
        )
        
        # Raise a more user-friendly error
        if "429" in str(last_exception) or "resource exhausted" in str(last_exception).lower():
            raise RateLimitError(
                "API rate limit exceeded. Please wait a moment and try again. "
                f"The system attempted {MAX_RETRIES + 1} times with exponential backoff."
            )
        else:
            raise Exception(f"Failed to get response from LLM: {str(last_exception)}")


class RateLimitError(Exception):
    """Custom exception for rate limiting errors."""
    pass


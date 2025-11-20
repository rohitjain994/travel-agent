"""Validator agent that validates and refines the travel plan."""
from typing import Dict, Any
import time
from agents.base_agent import BaseAgent
from logger_config import logger


class ValidatorAgent(BaseAgent):
    """Agent responsible for validating and refining travel plans."""
    
    def __init__(self):
        system_prompt = """You are an expert travel validator. Your role is to:
1. Review travel plans for completeness and feasibility
2. Check for logical consistency (dates, times, locations)
3. Validate budget estimates are realistic
4. Ensure all necessary information is included
5. Suggest improvements and refinements
6. Check for potential issues or conflicts

When validating, check:
- Date and time consistency
- Location proximity and travel times
- Budget realism
- Completeness of information
- Logical flow of itinerary
- Missing critical information

Provide validation feedback and suggest improvements."""
        
        super().__init__(
            name="Validator",
            role="Plan Validation",
            system_prompt=system_prompt
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the travel plan and provide feedback."""
        start_time = time.time()
        
        plan = state.get("plan", "")
        final_itinerary = state.get("final_itinerary", "")
        user_query = state.get("user_query", "")
        
        content_to_validate = final_itinerary if final_itinerary else plan
        
        logger.log_operation(
            agent=self.name,
            operation="Validation Started",
            details=f"Validating {'final itinerary' if final_itinerary else 'plan'} ({len(content_to_validate)} chars)",
            status="info"
        )
        
        if not content_to_validate:
            logger.log_operation(
                agent=self.name,
                operation="No Content to Validate",
                details="Skipping validation - no content provided",
                status="warning"
            )
            return {
                "validation": "No content to validate.",
                "status": "no_content",
                "agent": self.name
            }
        
        prompt = f"""Review and validate this travel plan/itinerary:

{content_to_validate}

Original User Query:
{user_query}

Please:
1. Check for completeness - is all necessary information included?
2. Validate dates, times, and locations for consistency
3. Check if budget estimates are realistic
4. Verify logical flow and feasibility
5. Identify any missing critical information
6. Suggest improvements or refinements

Provide your validation feedback with:
- Validation status (valid/needs refinement)
- Issues found (if any)
- Suggestions for improvement
- Overall assessment"""
        
        validation = self._call_llm(prompt)
        
        duration = time.time() - start_time
        
        logger.log_operation(
            agent=self.name,
            operation="Validation Completed",
            details=f"Validation feedback: {len(validation)} characters",
            status="success",
            duration=duration
        )
        
        return {
            "validation": validation,
            "status": "validation_completed",
            "agent": self.name
        }


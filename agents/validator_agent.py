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

Please provide a comprehensive validation that ALWAYS includes:

1. **Validation Status**: Overall assessment (excellent/good/needs improvement)
2. **Issues Found**: Any problems, inconsistencies, or missing information
3. **Suggestions for Improvement**: Specific ways to enhance the plan
4. **Next Steps for Improvement** (REQUIRED - always include this section):
   - What additional details or information would make this plan more promising?
   - What specific actions should the user take to improve the plan?
   - What questions should be answered to refine the itinerary?
   - What research or decisions are still needed?
   - How can the budget be optimized?
   - What alternatives or backup plans should be considered?
   - What cultural or local insights would enhance the experience?

IMPORTANT: Always provide actionable, specific next steps even if the plan is already good. Focus on:
- Missing information that would make the plan better
- Specific improvements that could be made
- Questions that need answers
- Research that could enhance the plan
- Details that would make execution smoother

Format your response with clear sections, especially highlighting the "Next Steps for Improvement" section."""
        
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


"""Executor agent that executes the travel plan and coordinates actions."""
from typing import Dict, Any
import time
from agents.base_agent import BaseAgent
from logger_config import logger


class ExecutorAgent(BaseAgent):
    """Agent responsible for executing the travel plan and coordinating actions."""
    
    def __init__(self):
        system_prompt = """You are an expert travel executor. Your role is to:
1. Take the travel plan and research results
2. Create a final, actionable travel itinerary
3. Synthesize information from planning and research
4. Provide step-by-step execution guide
5. Create a comprehensive final report with all details

When executing, provide:
- Final itinerary with all details filled in
- Booking recommendations with specific options
- Timeline and schedule
- Budget breakdown with actual prices
- Travel tips and reminders
- Emergency contacts and important information
- Packing suggestions based on destination and activities

Make the final output practical, actionable, and ready to use."""
        
        super().__init__(
            name="Executor",
            role="Plan Execution",
            system_prompt=system_prompt
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the travel plan by synthesizing plan and research."""
        start_time = time.time()
        
        plan = state.get("plan", "")
        research_results = state.get("research_results", "")
        user_query = state.get("user_query", "")
        
        logger.log_operation(
            agent=self.name,
            operation="Execution Started",
            details=f"Synthesizing plan ({len(plan)} chars) and research ({len(research_results)} chars)",
            status="info"
        )
        
        prompt = f"""Based on the travel plan and research results, create a final, executable travel itinerary:

Travel Plan:
{plan}

Research Results:
{research_results}

User Query:
{user_query}

Create a comprehensive final travel itinerary that includes:
1. Complete day-by-day schedule with specific times
2. Specific recommendations (hotels, restaurants, activities) with details
3. Booking information and links
4. Budget breakdown with actual prices
5. Travel tips and important reminders
6. Packing list suggestions
7. Emergency contacts and useful information
8. Alternative options in case of changes

9. **Next Steps for Enhancement** (REQUIRED - always include this section):
   - What additional information or details would make this plan more promising?
   - What specific improvements or refinements could be made?
   - What questions should be answered to further customize the itinerary?
   - What additional research or decisions are needed?
   - How can the user personalize this plan further?
   - What local insights or cultural tips would enhance the experience?
   - What backup plans or alternatives should be considered?
   - What budget optimizations or cost-saving opportunities exist?

IMPORTANT: Always end with a clear "Next Steps for Enhancement" section that provides actionable guidance on how to make this plan even better, even if the current plan is already comprehensive.

Make this a complete, ready-to-use travel guide with clear next steps for improvement."""
        
        final_itinerary = self._call_llm(prompt)
        
        duration = time.time() - start_time
        
        logger.log_operation(
            agent=self.name,
            operation="Execution Completed",
            details=f"Final itinerary created: {len(final_itinerary)} characters",
            status="success",
            duration=duration
        )
        
        return {
            "final_itinerary": final_itinerary,
            "status": "execution_completed",
            "agent": self.name
        }


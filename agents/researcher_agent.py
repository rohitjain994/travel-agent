"""Researcher agent that gathers information about flights, hotels, activities, etc."""
from typing import Dict, Any, List
import time
from agents.base_agent import BaseAgent
from logger_config import logger


class ResearcherAgent(BaseAgent):
    """Agent responsible for researching travel information."""
    
    def __init__(self):
        system_prompt = """You are an expert travel researcher. Your role is to:
1. Research flights, hotels, restaurants, activities, and attractions
2. Provide detailed information including prices, availability, ratings, and reviews
3. Compare options and make recommendations
4. Provide practical information (addresses, contact info, booking links)
5. Consider user preferences and budget constraints

When researching, provide:
- Multiple options with pros and cons
- Price ranges and availability
- Ratings and reviews
- Booking information
- Location details
- Best times to visit/book

Be thorough and provide actionable information."""
        
        super().__init__(
            name="Researcher",
            role="Travel Research",
            system_prompt=system_prompt
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Research travel information based on tasks."""
        start_time = time.time()
        
        research_tasks = state.get("research_tasks", "")
        plan = state.get("plan", "")
        user_query = state.get("user_query", "")
        
        logger.log_operation(
            agent=self.name,
            operation="Execution Started",
            details=f"Research tasks: {len(research_tasks.split('\n')) if research_tasks else 0} items",
            status="info"
        )
        
        if not research_tasks:
            logger.log_operation(
                agent=self.name,
                operation="No Research Tasks",
                details="Skipping research - no tasks provided",
                status="warning"
            )
            return {
                "research_results": "No research tasks provided.",
                "status": "no_tasks",
                "agent": self.name
            }
        
        logger.log_operation(
            agent=self.name,
            operation="Conducting Research",
            details=f"Researching {len(research_tasks.split('\n'))} tasks",
            status="info"
        )
        
        prompt = f"""Based on the travel plan and research tasks, provide detailed research results:

Travel Plan:
{plan}

Research Tasks:
{research_tasks}

User Query:
{user_query}

For each research task, provide:
1. Multiple options (at least 2-3 per category)
2. Prices and availability
3. Ratings and reviews
4. Pros and cons
5. Recommendations
6. Booking information (websites, contact info)

Format your response clearly with sections for each research category (flights, hotels, activities, restaurants, etc.)."""
        
        research_results = self._call_llm(prompt)
        
        duration = time.time() - start_time
        
        logger.log_operation(
            agent=self.name,
            operation="Research Completed",
            details=f"Results length: {len(research_results)} characters",
            status="success",
            duration=duration
        )
        
        return {
            "research_results": research_results,
            "status": "research_completed",
            "agent": self.name
        }


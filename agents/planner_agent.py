"""Planner agent that creates travel plans based on user requirements."""
from typing import Dict, Any
import time
from agents.base_agent import BaseAgent
from logger_config import logger


class PlannerAgent(BaseAgent):
    """Agent responsible for creating detailed travel plans."""
    
    def __init__(self):
        system_prompt = """You are an expert travel planner. Your role is to:
1. Analyze user travel requirements (destination, dates, budget, preferences)
2. Create a comprehensive, day-by-day travel itinerary
3. Break down the plan into actionable steps
4. Consider budget constraints, time availability, and user preferences
5. Identify what information needs to be researched (flights, hotels, activities)

When creating a plan, structure it as:
- Overview: Summary of the trip
- Day-by-day itinerary with activities
- Required research tasks: List what needs to be researched (flights, hotels, restaurants, attractions)
- Budget breakdown: Estimated costs by category
- Recommendations: Tips and suggestions

Output your plan in a clear, structured format."""
        
        super().__init__(
            name="Planner",
            role="Travel Planning",
            system_prompt=system_prompt
        )
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a travel plan based on user requirements."""
        start_time = time.time()
        
        logger.log_operation(
            agent=self.name,
            operation="Execution Started",
            details=f"Processing user query: {state.get('user_query', '')[:100]}",
            status="info"
        )
        
        try:
            user_query = state.get("user_query", "")
            conversation_history = state.get("conversation_history", [])
            
            # Build context from conversation history
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])
            
            logger.log_operation(
                agent=self.name,
                operation="Creating Travel Plan",
                details=f"Context length: {len(context)} chars, History items: {len(conversation_history)}",
                status="info"
            )
            
            prompt = f"""Based on the following conversation, create a detailed travel plan:

{context}

Current Request: {user_query}

Create a comprehensive travel plan including:
1. Trip overview and summary
2. Day-by-day itinerary
3. Research tasks needed (flights, hotels, activities, restaurants)
4. Budget estimates
5. Recommendations

Format your response clearly with sections."""
            
            plan = self._call_llm(prompt)
            
            logger.log_operation(
                agent=self.name,
                operation="Plan Created",
                details=f"Plan length: {len(plan)} characters",
                status="success"
            )
            
            # Extract research tasks from the plan
            logger.log_operation(
                agent=self.name,
                operation="Extracting Research Tasks",
                details="Analyzing plan to identify research requirements",
                status="info"
            )
            
            research_prompt = f"""From this travel plan, extract a list of specific research tasks needed:

{plan}

List each research task as a separate item. For example:
- Research flights from [origin] to [destination] for [dates]
- Research hotels in [location] for [dates]
- Research restaurants in [location] with [preferences]
- Research activities/attractions in [location]

Output only the list of research tasks, one per line."""
            
            research_tasks = self._call_llm(research_prompt)
            
            duration = time.time() - start_time
            
            logger.log_operation(
                agent=self.name,
                operation="Execution Completed",
                details=f"Research tasks identified: {len(research_tasks.split('\\n'))} items",
                status="success",
                duration=duration
            )
            
            return {
                "plan": plan,
                "research_tasks": research_tasks,
                "status": "plan_created",
                "agent": self.name
            }
        except Exception as e:
            duration = time.time() - start_time
            logger.log_operation(
                agent=self.name,
                operation="Execution Failed",
                details=f"Error: {str(e)}",
                status="error",
                duration=duration
            )
            raise


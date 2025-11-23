"""LangGraph orchestrator for coordinating multi-agent travel planning."""
from typing import Dict, Any, TypedDict
import time
from langgraph.graph import StateGraph, END
from travel_agent.agents import PlannerAgent, ResearcherAgent, ExecutorAgent, ValidatorAgent
from travel_agent.core.logger_config import logger


class TravelAgentState(TypedDict):
    """State structure for the travel agent workflow."""
    user_query: str
    conversation_history: list
    plan: str
    research_tasks: str
    research_results: str
    final_itinerary: str
    validation: str
    status: str
    current_agent: str
    iteration: int


class TravelAgentOrchestrator:
    """Orchestrator for coordinating multi-agent travel planning workflow."""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.executor = ExecutorAgent()
        self.validator = ValidatorAgent()
        
        # Build the graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(TravelAgentState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("researcher", self._researcher_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("validator", self._validator_node)
        
        # Define the flow
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "executor")
        workflow.add_edge("executor", "validator")
        workflow.add_edge("validator", END)
        
        return workflow
    
    def _planner_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """Execute planner agent."""
        logger.log_state_transition(
            from_agent="Orchestrator",
            to_agent="Planner",
            state_summary="Starting planning phase"
        )
        result = self.planner.execute(state)
        logger.log_state_transition(
            from_agent="Planner",
            to_agent="Researcher",
            state_summary="Planning completed, moving to research"
        )
        return {
            "plan": result.get("plan", ""),
            "research_tasks": result.get("research_tasks", ""),
            "status": result.get("status", ""),
            "current_agent": "planner",
            "iteration": state.get("iteration", 0) + 1
        }
    
    def _researcher_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """Execute researcher agent."""
        logger.log_state_transition(
            from_agent="Planner",
            to_agent="Researcher",
            state_summary="Starting research phase"
        )
        result = self.researcher.execute(state)
        logger.log_state_transition(
            from_agent="Researcher",
            to_agent="Executor",
            state_summary="Research completed, moving to execution"
        )
        return {
            "research_results": result.get("research_results", ""),
            "status": result.get("status", ""),
            "current_agent": "researcher",
            "iteration": state.get("iteration", 0) + 1
        }
    
    def _executor_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """Execute executor agent."""
        logger.log_state_transition(
            from_agent="Researcher",
            to_agent="Executor",
            state_summary="Starting execution phase"
        )
        result = self.executor.execute(state)
        logger.log_state_transition(
            from_agent="Executor",
            to_agent="Validator",
            state_summary="Execution completed, moving to validation"
        )
        return {
            "final_itinerary": result.get("final_itinerary", ""),
            "status": result.get("status", ""),
            "current_agent": "executor",
            "iteration": state.get("iteration", 0) + 1
        }
    
    def _validator_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """Execute validator agent."""
        logger.log_state_transition(
            from_agent="Executor",
            to_agent="Validator",
            state_summary="Starting validation phase"
        )
        result = self.validator.execute(state)
        logger.log_state_transition(
            from_agent="Validator",
            to_agent="END",
            state_summary="Validation completed, workflow finished"
        )
        return {
            "validation": result.get("validation", ""),
            "status": result.get("status", ""),
            "current_agent": "validator",
            "iteration": state.get("iteration", 0) + 1
        }
    
    def process_query(self, user_query: str, conversation_history: list = None) -> Dict[str, Any]:
        """Process a user query through the multi-agent workflow."""
        start_time = time.time()
        
        logger.log_operation(
            agent="Orchestrator",
            operation="Workflow Started",
            details=f"Processing query: {user_query[:100]}",
            status="info"
        )
        
        if conversation_history is None:
            conversation_history = []
        
        initial_state: TravelAgentState = {
            "user_query": user_query,
            "conversation_history": conversation_history,
            "plan": "",
            "research_tasks": "",
            "research_results": "",
            "final_itinerary": "",
            "validation": "",
            "status": "initialized",
            "current_agent": "",
            "iteration": 0
        }
        
        try:
            # Run the graph
            final_state = self.app.invoke(initial_state)
            
            duration = time.time() - start_time
            
            logger.log_operation(
                agent="Orchestrator",
                operation="Workflow Completed",
                details=f"Total duration: {duration:.2f}s, Iterations: {final_state.get('iteration', 0)}",
                status="success",
                duration=duration
            )
            
            return final_state
            
        except Exception as e:
            duration = time.time() - start_time
            logger.log_operation(
                agent="Orchestrator",
                operation="Workflow Failed",
                details=f"Error: {str(e)}",
                status="error",
                duration=duration
            )
            raise


"""Graph construction and routing logic for the agent."""
from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .state import AgentState, IntentType
from .nodes import AgentNodes
from ..utils.logger import get_logger

logger = get_logger(__name__)


def create_agent_graph(agent_nodes: AgentNodes):
    """
    Create the LangGraph workflow for the agent.
    
    Args:
        agent_nodes: Configured agent nodes instance
        
    Returns:
        Compiled graph ready for execution
    """
    logger.info("Creating agent graph...")
    
    # Initialize the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("intent_recognition", agent_nodes.intent_recognition_node)
    workflow.add_node("simple_interaction", agent_nodes.simple_interaction_node)
    workflow.add_node("plan_generation", agent_nodes.plan_generation_node)
    workflow.add_node("execution", agent_nodes.execution_node)
    workflow.add_node("analysis", agent_nodes.analysis_node)
    workflow.add_node("answer_generation", agent_nodes.answer_generation_node)
    
    logger.info("Added all nodes to graph")
    
    # Define routing functions
    def route_after_intent(
        state: AgentState
    ) -> Literal["simple_interaction", "plan_generation"]:
        """
        Route after intent recognition.
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        intent = state["detected_intent"]
        logger.info(f"Routing after intent: {intent}")
        
        if intent == IntentType.SIMPLE_INTERACTION:
            return "simple_interaction"
        else:
            return "plan_generation"
    
    def route_after_execution(
        state: AgentState
    ) -> Literal["execution", "analysis"]:
        """
        Route after execution step.
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        current_step = state["current_step_index"]
        total_steps = len(state["plan"]["steps"])
        
        logger.info(f"Routing after execution: step {current_step}/{total_steps}")
        
        if current_step < total_steps:
            return "execution"
        else:
            return "analysis"
    
    def route_after_analysis(
        state: AgentState
    ) -> Literal["answer_generation", "plan_generation"]:
        """
        Route after information analysis.
        
        Args:
            state: Current agent state
            
        Returns:
            Next node name
        """
        is_sufficient = state["is_information_sufficient"]
        logger.info(f"Routing after analysis: sufficient={is_sufficient}")
        
        if is_sufficient:
            return "answer_generation"
        else:
            # Information not sufficient, replan
            logger.info("Information insufficient, replanning...")
            # Increment replan counter
            return "plan_generation"
    
    # Set entry point
    workflow.set_entry_point("intent_recognition")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "intent_recognition",
        route_after_intent,
        {
            "simple_interaction": "simple_interaction",
            "plan_generation": "plan_generation"
        }
    )
    
    # Simple interaction goes directly to END
    workflow.add_edge("simple_interaction", END)
    
    # Plan generation goes to execution
    workflow.add_edge("plan_generation", "execution")
    
    # Execution can loop or go to analysis
    workflow.add_conditional_edges(
        "execution",
        route_after_execution,
        {
            "execution": "execution",
            "analysis": "analysis"
        }
    )
    
    # Analysis can go to answer or back to planning
    workflow.add_conditional_edges(
        "analysis",
        route_after_analysis,
        {
            "answer_generation": "answer_generation",
            "plan_generation": "plan_generation"
        }
    )
    
    # Answer generation goes to END
    workflow.add_edge("answer_generation", END)
    
    logger.info("Added all edges and routing logic")
    
    # Add checkpointer for state persistence
    checkpointer = MemorySaver()
    
    # Compile the graph with recursion limit
    app = workflow.compile(
        checkpointer=checkpointer,
        # Increase recursion limit to handle complex queries
        # But prevent infinite loops with max_replan_attempts in analysis node
    )
    
    logger.info("Graph compiled successfully")
    
    return app


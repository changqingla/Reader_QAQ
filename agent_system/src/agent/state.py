"""State definitions for the agent system."""
from enum import Enum
from typing import List, Optional, TypedDict

from langchain_core.messages import BaseMessage


class IntentType(str, Enum):
    """Enumeration of supported task intent types."""
    
    SIMPLE_INTERACTION = "simple_interaction"
    COMPARISON_EVALUATION = "comparison_evaluation"
    SUMMARY_EXTRACTION = "summary_extraction"
    COMPLIANCE_MATCHING = "compliance_matching"
    KNOWLEDGE_REASONING = "knowledge_reasoning"
    TEMPLATE_GENERATION = "template_generation"


class StepType(str, Enum):
    """Enumeration of plan step types."""
    
    RECALL = "recall"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"


class PlanStep(TypedDict):
    """Definition of a single plan step."""
    
    title: str
    step_type: StepType


class Plan(TypedDict):
    """Definition of execution plan."""
    
    locale: str
    thought: str
    title: str
    steps: List[PlanStep]


class QAPair(TypedDict):
    """A question-answer pair generated during deep thinking mode."""
    
    step_index: int
    question: str
    answer: str
    recall_query: Optional[str]


class ExecutionResult(TypedDict):
    """Result of executing a single step."""
    
    step_index: int
    step_title: str
    step_type: StepType
    tool_used: Optional[str]
    query: Optional[str]
    result: str
    error: Optional[str]


class ToolDecision(TypedDict):
    """Decision about tool usage."""
    
    need_tool: bool
    tool_name: Optional[str]
    query: Optional[str]
    reasoning: str


class InformationAnalysis(TypedDict):
    """Result of information sufficiency analysis."""
    
    is_sufficient: bool
    analysis: str
    missing_aspects: List[str]
    suggested_actions: List[str]


class AgentState(TypedDict):
    """
    Complete state for the agent system.
    
    This state is passed between all nodes in the LangGraph workflow.
    """
    
    # User inputs
    user_query: str
    mode_type: Optional[IntentType]
    enable_web_search: bool
    deep_thinking: bool  # Enable deep thinking mode with QA pairs
    
    # Direct content mode (for small documents)
    direct_content: Optional[str]  # Full document content provided by user
    use_direct_content: bool  # Whether to use direct content instead of recall
    content_token_count: Optional[int]  # Token count of the direct content
    
    # Intent recognition
    detected_intent: IntentType
    
    # Planning
    plan: Optional[Plan]
    current_step_index: int
    replan_count: int  # Track number of replanning attempts
    
    # Execution
    execution_results: List[ExecutionResult]
    collected_information: str  # Used in fast mode
    qa_pairs: List[QAPair]  # Used in deep thinking mode
    
    # Analysis
    is_information_sufficient: bool
    analysis_result: Optional[InformationAnalysis]
    
    # Final output
    final_answer: str
    
    # Message history for conversation context
    messages: List[BaseMessage]
    
    # Session and context management
    session_id: Optional[str]
    session_history: Optional[List]  # Injected session history (List[Message])
    session_tokens: Optional[int]  # Token count of injected history
    
    # Recall configuration (dynamic overrides)
    recall_index_names: Optional[List[str]]  # Override for recall index names
    recall_doc_ids: Optional[List[str]]  # Override for recall document IDs
    
    # Metadata
    start_time: Optional[float]
    error: Optional[str]


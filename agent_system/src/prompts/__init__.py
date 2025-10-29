"""Prompt templates for the agent system."""
from .intent_prompts import INTENT_RECOGNITION_PROMPT

# Import from planning module (all tasks now support fast/deep modes)
from .planning import (
    get_planning_prompt,
    # Fast mode prompts
    SUMMARY_FAST_MODE_PROMPT,
    COMPARISON_FAST_MODE_PROMPT,
    COMPLIANCE_FAST_MODE_PROMPT,
    KNOWLEDGE_FAST_MODE_PROMPT,
    TEMPLATE_FAST_MODE_PROMPT,
    # Deep thinking mode prompts
    SUMMARY_DEEP_THINKING_PROMPT,
    COMPARISON_DEEP_THINKING_PROMPT,
    COMPLIANCE_DEEP_THINKING_PROMPT,
    KNOWLEDGE_DEEP_THINKING_PROMPT,
    TEMPLATE_DEEP_THINKING_PROMPT,
)
from .execution_prompts import TOOL_EXECUTION_PROMPT
from .analysis_prompts import INFORMATION_ANALYSIS_PROMPT
from .answer_prompts import (
    SIMPLE_INTERACTION_PROMPT,
    COMPARISON_ANSWER_PROMPT,
    SUMMARY_ANSWER_PROMPT,
    COMPLIANCE_ANSWER_PROMPT,
    KNOWLEDGE_ANSWER_PROMPT,
    TEMPLATE_ANSWER_PROMPT,
    get_answer_prompt
)
from .deep_thinking_prompts import (
    SUB_QUESTION_ANSWER_PROMPT,
    FAST_MODE_ANSWER_PROMPT,
    get_sub_question_context
)

__all__ = [
    # Intent recognition
    "INTENT_RECOGNITION_PROMPT",
    
    # Planning prompts (all tasks support fast/deep modes)
    "get_planning_prompt",
    # Fast mode
    "SUMMARY_FAST_MODE_PROMPT",
    "COMPARISON_FAST_MODE_PROMPT",
    "COMPLIANCE_FAST_MODE_PROMPT",
    "KNOWLEDGE_FAST_MODE_PROMPT",
    "TEMPLATE_FAST_MODE_PROMPT",
    # Deep thinking mode
    "SUMMARY_DEEP_THINKING_PROMPT",
    "COMPARISON_DEEP_THINKING_PROMPT",
    "COMPLIANCE_DEEP_THINKING_PROMPT",
    "KNOWLEDGE_DEEP_THINKING_PROMPT",
    "TEMPLATE_DEEP_THINKING_PROMPT",
    
    # Execution and analysis
    "TOOL_EXECUTION_PROMPT",
    "INFORMATION_ANALYSIS_PROMPT",
    
    # Simple interaction
    "SIMPLE_INTERACTION_PROMPT",
    
    # Answer prompts
    "COMPARISON_ANSWER_PROMPT",
    "SUMMARY_ANSWER_PROMPT",
    "COMPLIANCE_ANSWER_PROMPT",
    "KNOWLEDGE_ANSWER_PROMPT",
    "TEMPLATE_ANSWER_PROMPT",
    "get_answer_prompt",
    
    # Deep thinking sub-question answering
    "SUB_QUESTION_ANSWER_PROMPT",
    "FAST_MODE_ANSWER_PROMPT",
    "get_sub_question_context"
]


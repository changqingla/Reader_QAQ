"""Planning prompts for different task types and modes.

This module provides a unified interface to access planning prompts for all
supported task types in both fast and deep thinking modes.
"""

# Import all task-specific prompts
from .summary_extraction import (
    SUMMARY_FAST_MODE_PROMPT,
    SUMMARY_DEEP_THINKING_PROMPT,
)
from .comparison_evaluation import (
    COMPARISON_FAST_MODE_PROMPT,
    COMPARISON_DEEP_THINKING_PROMPT,
)
from .compliance_matching import (
    COMPLIANCE_FAST_MODE_PROMPT,
    COMPLIANCE_DEEP_THINKING_PROMPT,
)
from .knowledge_reasoning import (
    KNOWLEDGE_FAST_MODE_PROMPT,
    KNOWLEDGE_DEEP_THINKING_PROMPT,
)
from .template_generation import (
    TEMPLATE_FAST_MODE_PROMPT,
    TEMPLATE_DEEP_THINKING_PROMPT,
)


def get_planning_prompt(intent_type, deep_thinking: bool = False) -> str:
    """
    Get the appropriate planning prompt based on intent type and mode.
    
    Args:
        intent_type: The detected intent type (IntentType enum)
        deep_thinking: Whether to use deep thinking mode (default: False)
        
    Returns:
        The corresponding planning prompt template
        
    Raises:
        ValueError: If intent type is not supported
        
    Examples:
        >>> # Fast mode
        >>> prompt = get_planning_prompt(IntentType.SUMMARY_EXTRACTION, deep_thinking=False)
        >>> # Deep thinking mode
        >>> prompt = get_planning_prompt(IntentType.SUMMARY_EXTRACTION, deep_thinking=True)
    """
    # Import here to avoid circular dependency
    from ...agent.state import IntentType
    
    # Fast mode prompts map
    fast_mode_map = {
        IntentType.SUMMARY_EXTRACTION: SUMMARY_FAST_MODE_PROMPT,
        IntentType.COMPARISON_EVALUATION: COMPARISON_FAST_MODE_PROMPT,
        IntentType.COMPLIANCE_MATCHING: COMPLIANCE_FAST_MODE_PROMPT,
        IntentType.KNOWLEDGE_REASONING: KNOWLEDGE_FAST_MODE_PROMPT,
        IntentType.TEMPLATE_GENERATION: TEMPLATE_FAST_MODE_PROMPT,
    }
    
    # Deep thinking mode prompts map
    deep_thinking_map = {
        IntentType.SUMMARY_EXTRACTION: SUMMARY_DEEP_THINKING_PROMPT,
        IntentType.COMPARISON_EVALUATION: COMPARISON_DEEP_THINKING_PROMPT,
        IntentType.COMPLIANCE_MATCHING: COMPLIANCE_DEEP_THINKING_PROMPT,
        IntentType.KNOWLEDGE_REASONING: KNOWLEDGE_DEEP_THINKING_PROMPT,
        IntentType.TEMPLATE_GENERATION: TEMPLATE_DEEP_THINKING_PROMPT,
    }
    
    # Select appropriate map based on mode
    prompt_map = deep_thinking_map if deep_thinking else fast_mode_map
    
    # Get prompt
    if intent_type not in prompt_map:
        raise ValueError(
            f"Intent type '{intent_type}' is not supported for planning. "
            f"Supported types: {list(prompt_map.keys())}"
        )
    
    return prompt_map[intent_type]


__all__ = [
    # Main interface
    "get_planning_prompt",
    
    # Fast mode prompts
    "SUMMARY_FAST_MODE_PROMPT",
    "COMPARISON_FAST_MODE_PROMPT",
    "COMPLIANCE_FAST_MODE_PROMPT",
    "KNOWLEDGE_FAST_MODE_PROMPT",
    "TEMPLATE_FAST_MODE_PROMPT",
    
    # Deep thinking mode prompts
    "SUMMARY_DEEP_THINKING_PROMPT",
    "COMPARISON_DEEP_THINKING_PROMPT",
    "COMPLIANCE_DEEP_THINKING_PROMPT",
    "KNOWLEDGE_DEEP_THINKING_PROMPT",
    "TEMPLATE_DEEP_THINKING_PROMPT",
]

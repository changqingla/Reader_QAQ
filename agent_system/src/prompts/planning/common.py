"""Common components shared across all planning prompts.

This module provides reusable components to avoid code duplication across
different task types. All planning prompts should use these common elements.
"""

# ============ 公共前提（所有任务通用） ============
COMMON_PREREQUISITES = """**🔑 重要前提（必读）**：
1. **文档已在知识库中**：用户提到的文档（"这篇论文"、"这个文档"、"该报告"等）默认已经上传到系统的知识库中
2. **你可以主动检索**：使用recall工具可以检索知识库中的文档内容，用户不会在对话中粘贴完整文档
3. **指代词理解**：当用户说"这个/这篇/它"时，指的是已上传的文档，第一步应该检索文档信息来明确具体内容
4. **不要猜测**：不要假设用户指的是某篇知名文献，直接通过recall检索知识库即可获取实际文档"""


# ============ 步骤类型说明（所有任务统一） ============
COMMON_STEP_TYPES = """**步骤类型说明**：
- `recall`: 从知识库/文档中检索相关信息（必须明确说明检索什么内容）
- `analysis`: 分析、处理已收集的信息，不需要外部工具
- `synthesis`: 综合多个信息源形成结论，不需要外部工具"""


# ============ 输出要求（所有任务统一） ============
COMMON_OUTPUT_REQUIREMENTS = """**输出要求**：
必须输出严格的JSON格式，不要包含任何其他文本或markdown标记。"""


# ============ 快速模式通用指导 ============
FAST_MODE_GUIDELINES = """**快速模式规划要求**：
1. **简洁高效**：使用1-2个recall步骤一次性检索相关内容
2. **宽泛查询**：使用宽泛的查询语句，如"介绍一下文档的完整内容"、"介绍一下杭州"
3. **步骤总数**：2-3步（recall → synthesis 或 recall → recall → synthesis）
"""


# ============ 深度模式通用指导 ============
DEEP_THINKING_GUIDELINES = """**深度思考模式规划要求**：
1. **分层检索**：设计多个recall步骤，每步针对文档的不同方面
2. **生成QA对**：每个recall步骤会生成一个子问题的详细答案（QA对）
3. **步骤总数**：多个recall + analysis + synthesis）
4. **追求全面**：确保信息完整性和深度，适合多跳推理和长文档总结
5. **明确目标**：每个recall步骤的标题应清晰说明检索什么内容"""


# ============ JSON结构模板 ============
def get_json_structure(
    thought_guide: str,
    example_steps: list,
    mode: str = "fast"
) -> str:
    """
    Generate standard JSON structure template.
    
    Args:
        thought_guide: Task-specific thought process guide
        example_steps: Example steps for this task
        mode: "fast" or "deep" to adjust examples
        
    Returns:
        Formatted JSON structure string
    """
    steps_json = "[\n"
    for i, step in enumerate(example_steps):
        comma = "," if i < len(example_steps) - 1 else ""
        steps_json += f'    {{\n      "title": "{step["title"]}",\n      "step_type": "{step["step_type"]}"\n    }}{comma}\n'
    steps_json += "  ]"
    
    return f"""JSON结构：
{{{{
  "locale": "zh-CN",
  "thought": "{thought_guide}",
  "title": "任务的简洁标题（10-20字）,如果是recall需求则应该是检索什么内容",
  "steps": {steps_json}
}}}}"""


# ============ 标准快速模式步骤示例 ============
FAST_MODE_STANDARD_STEPS = [
    {"title": "文档的完整内容是什么？", "step_type": "recall"},
    {"title": "基于检索的信息回答用户的问题", "step_type": "synthesis"}
]


# ============ 标准深度模式步骤示例模板 ============
def get_deep_thinking_steps_example(domain_specific_steps: list) -> list:
    """
    Generate deep thinking mode steps with domain-specific middle steps.
    
    Args:
        domain_specific_steps: Task-specific recall steps (3-5 steps)
        
    Returns:
        Complete step list with analysis and synthesis
    """
    all_steps = domain_specific_steps + [
        {"title": "分析收集的信息", "step_type": "analysis"},
        {"title": "基于检索的信息回答用户的问题", "step_type": "synthesis"}
    ]
    return all_steps


# ============ 辅助函数：构建完整提示词 ============
def build_prompt(
    role: str,
    task_description: str,
    thinking_framework: str,
    mode_guidelines: str,
    mode_examples: str,
    json_structure: str
) -> str:
    """
    Build complete prompt from components.
    
    Args:
        role: Role description (e.g., "你是一个专业的XXX规划助手")
        task_description: Task-specific description
        thinking_framework: Task-specific thinking framework
        mode_guidelines: Fast or deep mode guidelines
        mode_examples: Task-specific examples for the mode
        json_structure: JSON structure template
        
    Returns:
        Complete formatted prompt
    """
    return f"""{role}

**用户问题**：
{{user_query}}

{COMMON_PREREQUISITES}

{task_description}

{thinking_framework}

{mode_guidelines}

{mode_examples}

{COMMON_STEP_TYPES}

{COMMON_OUTPUT_REQUIREMENTS}

{json_structure}

**请为上述用户问题生成执行计划（只输出JSON，不要有其他内容）**："""


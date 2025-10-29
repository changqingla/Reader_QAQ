"""Planning prompts for knowledge reasoning tasks."""

from .common import (
    COMMON_PREREQUISITES,
    COMMON_STEP_TYPES,
    COMMON_OUTPUT_REQUIREMENTS,
    FAST_MODE_GUIDELINES,
    DEEP_THINKING_GUIDELINES,
    build_prompt,
)

# ============ 任务特定内容 ============

TASK_DESCRIPTION = """**任务说明**：
知识问答与推理任务需要检索相关知识，并可能需要进行逻辑推理、因果分析等，最终回答用户的问题。"""

THINKING_FRAMEWORK = """**规划思考框架**：

1. **问题分析**：
   - 识别问题的类型（事实性问题、解释性问题、推理性问题等）
   - 确定问题涉及的知识领域
   - 分析问题的复杂度和层次

2. **知识定位**：
   - 确定需要检索的关键信息
   - 识别相关的概念、理论、原理
   - 确定知识的来源和权威性

3. **信息收集策略**：
   - 检索核心知识和定义
   - 收集背景信息和上下文
   - 获取相关案例和实证
   - 查找补充信息和边界情况

4. **推理分析方法**：
   - 逻辑推理（演绎、归纳、类比）
   - 因果分析（原因→结果、影响因素）
   - 关联分析（知识点之间的联系）
   - 综合判断（多角度权衡）

5. **答案构建**：
   - 组织知识结构
   - 形成完整论述
   - 提供证据支撑
   - 给出结论和建议"""

# ============ 快速模式提示词 ============

FAST_MODE_EXAMPLES = """**快速模式示例**：
- 知识查询：recall(相关知识和解释) → synthesis
- 概念理解：recall(概念定义和说明) → synthesis
- 问题解答：recall(问题相关的所有知识) → synthesis"""

FAST_MODE_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "分析问题类型、确定知识领域、设计检索策略（一次性获取相关知识）",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索问题相关的知识和解释",
      "step_type": "recall"
    }},
    {{
      "title": "综合形成答案",
      "step_type": "synthesis"
    }}
  ]
}}"""

KNOWLEDGE_FAST_MODE_PROMPT = build_prompt(
    role="你是一个专业的知识问答规划助手。用户需要进行知识问答和推理任务。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=FAST_MODE_GUIDELINES,
    mode_examples=FAST_MODE_EXAMPLES,
    json_structure=FAST_MODE_JSON_STRUCTURE
)

# ============ 深度思考模式提示词 ============

DEEP_THINKING_EXAMPLES = """**深度思考模式示例**：
- 复杂问答：recall(核心概念定义) → recall(背景知识) → recall(相关理论) → recall(实证案例) → recall(边界情况) → analysis(逻辑推理) → synthesis
- 因果分析：recall(现象描述) → recall(可能原因) → recall(影响因素) → recall(机制分析) → recall(实证支持) → analysis → synthesis
- 原理解释：recall(基本原理) → recall(工作机制) → recall(关键要素) → recall(应用场景) → recall(常见误解) → analysis → synthesis"""

DEEP_THINKING_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "详细分析：1)问题类型和复杂度 2)涉及的知识领域 3)分层检索计划（核心知识→背景→理论→案例→推理）4)推理策略 5)答案构建方式",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索核心概念和定义",
      "step_type": "recall"
    }},
    {{
      "title": "检索相关背景知识和上下文",
      "step_type": "recall"
    }},
    {{
      "title": "检索相关理论和原理",
      "step_type": "recall"
    }},
    {{
      "title": "检索实证案例和应用",
      "step_type": "recall"
    }},
    {{
      "title": "检索补充信息和边界情况",
      "step_type": "recall"
    }},
    {{
      "title": "逻辑推理和因果分析",
      "step_type": "analysis"
    }},
    {{
      "title": "综合形成完整答案",
      "step_type": "synthesis"
    }}
  ]
}}"""

KNOWLEDGE_DEEP_THINKING_PROMPT = build_prompt(
    role="你是一个专业的知识问答规划助手。用户需要进行知识问答和推理任务。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=DEEP_THINKING_GUIDELINES,
    mode_examples=DEEP_THINKING_EXAMPLES,
    json_structure=DEEP_THINKING_JSON_STRUCTURE
)


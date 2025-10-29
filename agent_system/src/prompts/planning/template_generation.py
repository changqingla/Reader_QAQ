"""Planning prompts for template generation tasks."""

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
模板化生成任务需要按照特定的格式和结构，生成文档、报告、代码或其他内容。"""

THINKING_FRAMEWORK = """**规划思考框架**：

1. **明确生成目标**：
   - 确定要生成的内容类型（文档、报告、代码、表格等）
   - 理解生成内容的用途和受众
   - 确定输出的格式要求（Markdown、JSON、代码等）

2. **确定模板结构**：
   - 识别模板的必要字段和可选字段
   - 确定内容的组织结构和层次
   - 明确格式规范和样式要求

3. **信息收集策略**：
   - 收集需要填充的数据和信息
   - 获取参考示例或最佳实践
   - 查找格式规范和标准
   - 收集相关的领域知识

4. **内容组织方法**：
   - 按模板结构组织信息
   - 确保内容的完整性和一致性
   - 遵循格式规范和约定

5. **质量保证**：
   - 检查内容的准确性
   - 验证格式的正确性
   - 确保输出的可用性"""

# ============ 快速模式提示词 ============

FAST_MODE_EXAMPLES = """**快速模式示例**：
- 文档生成：recall(模板结构和填充内容) → synthesis
- 报告生成：recall(报告格式和所需数据) → synthesis
- 代码生成：recall(代码规范和功能需求) → synthesis"""

FAST_MODE_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "分析生成目标、确定模板结构、设计检索策略（一次性获取模板和填充内容）",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索模板结构、格式规范和填充内容",
      "step_type": "recall"
    }},
    {{
      "title": "按模板生成内容",
      "step_type": "synthesis"
    }}
  ]
}}"""

TEMPLATE_FAST_MODE_PROMPT = build_prompt(
    role="你是一个专业的模板生成规划助手。用户需要进行模板化生成任务。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=FAST_MODE_GUIDELINES,
    mode_examples=FAST_MODE_EXAMPLES,
    json_structure=FAST_MODE_JSON_STRUCTURE
)

# ============ 深度思考模式提示词 ============

DEEP_THINKING_EXAMPLES = """**深度思考模式示例**：
- 技术文档：recall(文档模板和规范) → recall(功能详细信息) → recall(API接口说明) → recall(代码示例) → recall(最佳实践) → analysis(内容组织) → synthesis
- 项目报告：recall(报告模板结构) → recall(项目背景数据) → recall(执行情况) → recall(成果数据) → recall(问题和建议) → analysis → synthesis
- 代码生成：recall(代码规范) → recall(功能需求) → recall(设计模式) → recall(参考实现) → recall(测试用例) → analysis → synthesis"""

DEEP_THINKING_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "详细分析：1)生成目标和用途 2)模板结构分析 3)分层检索计划（模板→数据→示例→规范→质量）4)内容组织策略 5)格式要求",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索模板结构和格式规范",
      "step_type": "recall"
    }},
    {{
      "title": "检索需要填充的核心数据和信息",
      "step_type": "recall"
    }},
    {{
      "title": "检索参考示例和最佳实践",
      "step_type": "recall"
    }},
    {{
      "title": "检索领域知识和专业术语",
      "step_type": "recall"
    }},
    {{
      "title": "检索质量标准和检查项",
      "step_type": "recall"
    }},
    {{
      "title": "按模板组织和结构化内容",
      "step_type": "analysis"
    }},
    {{
      "title": "生成完整的格式化输出",
      "step_type": "synthesis"
    }}
  ]
}}"""

TEMPLATE_DEEP_THINKING_PROMPT = build_prompt(
    role="你是一个专业的模板生成规划助手。用户需要进行模板化生成任务。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=DEEP_THINKING_GUIDELINES,
    mode_examples=DEEP_THINKING_EXAMPLES,
    json_structure=DEEP_THINKING_JSON_STRUCTURE
)


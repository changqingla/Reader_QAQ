"""Planning prompts for summary extraction tasks."""

from .common import (
    FAST_MODE_GUIDELINES,
    DEEP_THINKING_GUIDELINES,
    build_prompt,
)

# ============ 任务特定内容 ============

TASK_DESCRIPTION = """**任务说明**：
文档总结任务的核心是全面理解文档内容，并根据文档类型和用户需求，选择合适的总结策略。总结应当注重**全面性**而非简单精简，确保重要信息不遗漏。"""

THINKING_FRAMEWORK = """**规划思考框架**（像专业人士一样思考）：

1. **文档获取策略**（首要步骤）：
   - 如果用户用指代词（"这个"、"这篇"），第一步必须是：检索文档基本信息（标题、类型、作者、摘要）
   - 如果用户明确提到文档关键词，直接检索相关内容
   - 对于长文档，分多次检索：先整体结构 → 各章节内容 → 关键细节

2. **文档类型识别**：（包括但不限于以下文档类型）
   - 学术论文 → 侧重：研究背景、问题定义、方法论、实验设计、结果分析、结论贡献、局限性
   - 技术文档 → 侧重：系统架构、功能模块、接口定义、使用方法、示例代码
   - 业务文档 → 侧重：业务目标、现状分析、解决方案、实施计划、预期效果、风险评估
   - 教程/指南 → 侧重：学习路径、操作步骤、原理讲解、常见问题、最佳实践
   - 政策/法规 → 侧重：适用范围、核心条款、权利义务、执行细则、处罚措施
   - 小说 → 侧重：主角、身世、背景、经历、结局
   
3. **总结目的分析**：
   - 用户是想快速了解大意（概述性总结）？还是需要深入理解细节（详细总结）？
   - 是否需要特定角度的信息（如：技术实现、业务价值、风险评估、适用场景）？
   - 是否需要保留关键数据、公式、引用、代码示例？

4. **内容层次划分**：
   - **宏观层**：文档主题、撰写目的、目标受众、整体结构（目录）
   - **核心层**：主要内容、关键概念、核心论点/方法/方案、重要发现
   - **细节层**：重要数据、实验结果、案例说明、代码示例、注意事项
   - **结论层**：总结陈述、建议行动、影响评估、未来展望

5. **多角度覆盖**：
   - **What**：文档讲了什么内容？核心主题是什么？
   - **Why**：为什么写这个文档？要解决什么问题？背景和动机是什么？
   - **How**：如何实现/操作/解决？具体方法、步骤、技术路线是什么？
   - **Result**：取得了什么结果？有哪些发现或产出？
   - **Impact**：有什么影响、价值、意义？适用范围和局限性？
   - **Context**：相关背景、前置知识、依赖关系、引用文献"""

# ============ 快速模式提示词 ============

FAST_MODE_EXAMPLES = """**快速模式示例**：
- 论文：recall(论文完整内容) → synthesis
- 技术文档：recall(文档整体内容和示例) → synthesis
- 业务方案：recall(方案所有要点) → synthesis"""

FAST_MODE_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "详细的思考过程，需要包含：1)用户问题分析 2)文档类型预判 3)总结策略（快速模式，一次性检索）4)检索查询设计",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索文档的完整内容和核心信息",
      "step_type": "recall"
    }},
    {{
      "title": "综合形成文档总结",
      "step_type": "synthesis"
    }}
  ]
}}"""

SUMMARY_FAST_MODE_PROMPT = build_prompt(
    role="你是一个专业的文档总结规划助手。用户需要从长文档中总结内容。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=FAST_MODE_GUIDELINES,
    mode_examples=FAST_MODE_EXAMPLES,
    json_structure=FAST_MODE_JSON_STRUCTURE
)

# ============ 深度思考模式提示词 ============

DEEP_THINKING_EXAMPLES = """**深度思考模式示例**：
- 论文：recall(基本信息+摘要) → recall(研究方法) → recall(实验结果) → recall(结论贡献) → analysis → synthesis
- 技术文档：recall(架构概述) → recall(核心模块) → recall(API接口) → recall(使用示例) → analysis → synthesis
- 业务方案：recall(背景目标) → recall(现状分析) → recall(解决方案) → recall(实施计划) → analysis → synthesis
- 小说：recall(主角身世) → recall(故事背景) → recall(主要经历) → recall(结局与主题) → analysis → synthesis
- 法律文书：recall(案件基本信息) → recall(事实依据) → recall(法律依据) → recall(判决结果) → analysis → synthesis
- 法规：recall(适用范围) → recall(核心条款) → recall(权利义务) → recall(处罚措施) → analysis → synthesis
- 合同：recall(合同基本信息) → recall(双方权利义务) → recall(违约责任) → recall(争议解决) → analysis → synthesis

**重要提醒**：每个recall步骤的标题应该清晰说明要检索什么内容，便于后续生成针对性的子问题答案。"""

DEEP_THINKING_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "详细的思考过程，需要包含：1)用户问题分析（是否有指代词，文档是否明确）2)文档类型预判 3)总结策略选择（深度思考模式，分层检索）4)分层检索计划（先检索什么，再检索什么，每步的目的）5)重点关注维度",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索文档基本信息（标题、作者、摘要、类型）",
      "step_type": "recall"
    }},
    {{
      "title": "检索文档主体内容的XX部分",
      "step_type": "recall"
    }},
    {{
      "title": "分析文档结构和核心论点",
      "step_type": "analysis"
    }},
    {{
      "title": "综合形成全面总结",
      "step_type": "synthesis"
    }}
  ]
}}"""

SUMMARY_DEEP_THINKING_PROMPT = build_prompt(
    role="你是一个专业的文档总结规划助手。用户需要从长文档中总结内容。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=DEEP_THINKING_GUIDELINES,
    mode_examples=DEEP_THINKING_EXAMPLES,
    json_structure=DEEP_THINKING_JSON_STRUCTURE
)

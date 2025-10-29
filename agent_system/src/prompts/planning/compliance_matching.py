"""Planning prompts for compliance matching tasks."""

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
合规/匹配判断任务需要评估某个对象、方案或行为是否符合特定的规则、标准、要求或条件。"""

THINKING_FRAMEWORK = """**规划思考框架**：

1. **明确判断对象**：
   - 识别需要判断的对象是什么（文档、方案、行为、产品等）
   - 确定对象的关键属性和特征
   
2. **确定参照标准**：
   - 识别需要遵循的规则、标准或要求
   - 明确标准的具体条款和细则
   - 确定判断的严格程度（完全符合/部分符合/不符合）

3. **信息收集策略**：
   - 收集判断对象的详细信息
   - 收集参照标准的完整内容
   - 收集相关的解释说明和案例

4. **逐项检查方法**：
   - 将标准拆解为具体的检查项
   - 逐项对比判断对象与标准
   - 记录符合情况和偏差

5. **判断结论**：
   - 总体符合性评估
   - 不符合项的详细说明
   - 整改建议（如有不符合项）"""

# ============ 快速模式提示词 ============

FAST_MODE_EXAMPLES = """**快速模式示例**：
- 合规检查：recall(对象信息和标准要求) → synthesis(符合性判断)
- 需求匹配：recall(方案内容和需求清单) → synthesis(匹配度分析)"""

FAST_MODE_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "分析判断对象、确定参照标准、设计检索策略（一次性获取对象和标准信息）",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索判断对象的信息和参照标准的要求",
      "step_type": "recall"
    }},
    {{
      "title": "综合判断符合性",
      "step_type": "synthesis"
    }}
  ]
}}"""

COMPLIANCE_FAST_MODE_PROMPT = build_prompt(
    role="你是一个专业的合规判断规划助手。用户需要进行合规或匹配判断任务。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=FAST_MODE_GUIDELINES,
    mode_examples=FAST_MODE_EXAMPLES,
    json_structure=FAST_MODE_JSON_STRUCTURE
)

# ============ 深度思考模式提示词 ============

DEEP_THINKING_EXAMPLES = """**深度思考模式示例**：
- 合规检查：recall(判断对象详细信息) → recall(标准完整条款) → recall(相关解释和案例) → recall(具体检查项) → analysis(逐项对比) → synthesis(符合性报告)
- 需求匹配：recall(需求详细清单) → recall(方案详细内容) → recall(功能对应关系) → recall(性能指标对比) → recall(特殊要求检查) → analysis → synthesis
- 政策适用：recall(政策适用范围) → recall(具体条款) → recall(实际情况) → recall(边界条件) → analysis → synthesis"""

DEEP_THINKING_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "详细分析：1)明确判断对象 2)确定参照标准 3)分层检索计划（对象信息→标准条款→检查项→边界情况）4)逐项检查策略 5)判断依据",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索判断对象的基本信息和详细内容",
      "step_type": "recall"
    }},
    {{
      "title": "检索参照标准的完整条款和要求",
      "step_type": "recall"
    }},
    {{
      "title": "检索标准的解释说明和适用案例",
      "step_type": "recall"
    }},
    {{
      "title": "检索具体检查项和边界条件",
      "step_type": "recall"
    }},
    {{
      "title": "逐项对比分析符合情况",
      "step_type": "analysis"
    }},
    {{
      "title": "综合形成符合性判断报告",
      "step_type": "synthesis"
    }}
  ]
}}"""

COMPLIANCE_DEEP_THINKING_PROMPT = build_prompt(
    role="你是一个专业的合规判断规划助手。用户需要进行合规或匹配判断任务。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=DEEP_THINKING_GUIDELINES,
    mode_examples=DEEP_THINKING_EXAMPLES,
    json_structure=DEEP_THINKING_JSON_STRUCTURE
)


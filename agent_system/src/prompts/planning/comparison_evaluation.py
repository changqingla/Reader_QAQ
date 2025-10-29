"""Planning prompts for comparison evaluation tasks."""

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
对比评估任务需要比较多个对象的特征、性能、优缺点等，最终给出客观的评估结果或建议。"""

THINKING_FRAMEWORK = """**规划思考框架**：

1. **明确对比对象**：
   - 识别需要对比的对象（产品、方案、技术、方法等）
   - 确定对比的数量（2个、3个或更多）
   
2. **确定对比维度**：
   - 性能指标（速度、准确率、吞吐量等）
   - 成本因素（价格、维护成本、学习成本等）
   - 易用性（用户体验、文档完善度、上手难度等）
   - 可扩展性（灵活性、可定制性、生态系统等）
   - 适用场景（最佳实践、使用限制、特殊需求等）

3. **信息收集策略**：
   - 每个对象的基本信息和特征
   - 各对象在每个维度的表现
   - 优缺点分析
   - 实际使用案例和评价

4. **对比分析方法**：
   - 多维度量化对比（表格、矩阵）
   - 优劣势分析（SWOT）
   - 适用场景匹配
   
5. **结论和建议**：
   - 综合评估结果
   - 针对不同需求的推荐
   - 选择建议和注意事项"""

# ============ 快速模式提示词 ============

FAST_MODE_EXAMPLES = """**快速模式示例**：
- 产品对比：recall(所有产品的特征和差异对比信息) → synthesis
- 技术方案对比：recall(各方案的优缺点和适用场景) → synthesis"""

FAST_MODE_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "分析对比对象、确定对比维度、设计检索策略（一次性获取所有对比信息）",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索所有对比对象的特征、优缺点和对比信息",
      "step_type": "recall"
    }},
    {{
      "title": "综合对比分析和评估",
      "step_type": "synthesis"
    }}
  ]
}}"""

COMPARISON_FAST_MODE_PROMPT = build_prompt(
    role="你是一个专业的对比评估规划助手。用户需要进行对比评估任务。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=FAST_MODE_GUIDELINES,
    mode_examples=FAST_MODE_EXAMPLES,
    json_structure=FAST_MODE_JSON_STRUCTURE
)

# ============ 深度思考模式提示词 ============

DEEP_THINKING_EXAMPLES = """**深度思考模式示例**：
- 产品对比：recall(对比对象基本信息) → recall(对象A详细特征) → recall(对象B详细特征) → recall(性能数据对比) → recall(用户评价和案例) → analysis(多维度对比) → synthesis
- 技术方案对比：recall(各方案概述) → recall(技术架构对比) → recall(性能表现对比) → recall(成本和易用性对比) → recall(适用场景分析) → analysis → synthesis
- 算法对比：recall(算法原理) → recall(时间复杂度对比) → recall(空间复杂度对比) → recall(实际性能测试) → recall(应用场景) → analysis → synthesis"""

DEEP_THINKING_JSON_STRUCTURE = """JSON结构：
{{
  "locale": "zh-CN",
  "thought": "详细分析：1)识别对比对象 2)确定对比维度 3)分层检索计划（基本信息→各对象详细特征→对比维度数据→案例评价）4)对比分析策略 5)评估标准",
  "title": "任务的简洁标题（10-20字）",
  "steps": [
    {{
      "title": "检索对比对象的基本信息和概述",
      "step_type": "recall"
    }},
    {{
      "title": "检索对象A的详细特征和性能数据",
      "step_type": "recall"
    }},
    {{
      "title": "检索对象B的详细特征和性能数据",
      "step_type": "recall"
    }},
    {{
      "title": "检索各对象在关键维度的对比数据",
      "step_type": "recall"
    }},
    {{
      "title": "检索使用案例和用户评价",
      "step_type": "recall"
    }},
    {{
      "title": "多维度对比分析",
      "step_type": "analysis"
    }},
    {{
      "title": "综合评估和推荐建议",
      "step_type": "synthesis"
    }}
  ]
}}"""

COMPARISON_DEEP_THINKING_PROMPT = build_prompt(
    role="你是一个专业的对比评估规划助手。用户需要进行对比评估任务。",
    task_description=TASK_DESCRIPTION,
    thinking_framework=THINKING_FRAMEWORK,
    mode_guidelines=DEEP_THINKING_GUIDELINES,
    mode_examples=DEEP_THINKING_EXAMPLES,
    json_structure=DEEP_THINKING_JSON_STRUCTURE
)


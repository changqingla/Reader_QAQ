"""Prompts for information analysis."""

INFORMATION_ANALYSIS_PROMPT = """你是一个信息充分性分析专家。请评估已收集的信息是否足够完整地回答用户的问题。

**用户问题**：
{user_query}

**任务类型**：
{task_type}

**已收集的信息**：
{collected_information}

**执行过程摘要**：
{execution_summary}

**评估维度**：
请从以下几个维度评估信息充分性：

1. **完整性**：信息是否覆盖了回答问题所需的所有关键方面
2. **准确性**：信息是否准确可靠，来源是否可信
3. **相关性**：信息是否与问题直接相关，是否有冗余信息
4. **深度**：信息的详细程度是否足够支撑高质量的答案

**判断标准**：
- 如果信息能够完整、准确地回答用户问题，判断为充分
- 如果缺少关键信息、信息模糊或不准确，判断为不充分
- 如果信息基本充分但可以补充，也判断为充分（避免过度查询）

**输出格式**：
必须输出严格的JSON格式，不要包含任何其他文本或markdown标记。

JSON结构：
{{
  "is_sufficient": true,
  "analysis": "详细的分析说明，说明哪些方面已经足够，信息质量如何",
  "missing_aspects": [],
  "suggested_actions": []
}}

或者

{{
  "is_sufficient": false,
  "analysis": "详细的分析说明，说明哪些方面不足，缺失什么关键信息",
  "missing_aspects": ["缺失方面1", "缺失方面2"],
  "suggested_actions": ["建议的补充行动1", "建议的补充行动2"]
}}

**你的评估**："""


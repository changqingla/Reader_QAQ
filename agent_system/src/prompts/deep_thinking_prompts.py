"""Prompts for deep thinking mode with QA pairs."""


SUB_QUESTION_ANSWER_PROMPT = """你是一个专业的文档分析助手。当前处于深度思考模式，需要基于召回的文档内容回答一个具体的子问题。

**用户原始问题**：
{user_query}

**当前子问题（Step {step_index}/{total_steps}）**：
{sub_question}

**已有上下文信息**（前面步骤的QA对）：
{previous_qa_context}

**召回的文档内容**：
{recalled_content}

**任务说明**：
请基于召回的文档内容，详细回答当前子问题。你的回答将作为该步骤的输出，与其他步骤的回答一起用于生成最终答案。

**回答要求**：
1. **保留关键信息**：数字、百分比、日期、人名、专业术语、公式、代码片段等
2. **结构清晰**：如果内容较多，使用小标题或分点陈述
3. **适度详细**：既要全面覆盖要点，又要避免过度冗长（建议200-800字）
4. **准确引用**：如有重要引用、出处、图表编号，请保留
5. **上下文一致**：参考前面步骤的回答，保持术语和表述的一致性
6. **如实回答**：如果召回内容不足以回答问题，明确说明缺少哪些信息

**输出格式**：
直接输出答案内容，不需要额外的格式标记或说明文字。

**示例输出**：

论文提出了基于Transformer的多模态融合方法，核心创新点包括：

1. **跨模态注意力机制**：设计了Cross-Modal Attention Layer，能够捕获视觉和文本特征之间的细粒度对应关系。具体实现上，使用Q-K-V结构，其中Q来自文本编码器，K和V来自视觉编码器。

2. **层次化融合策略**：采用三阶段融合：
   - 低层特征融合（Early Fusion）：在特征提取阶段融合
   - 中层特征融合（Middle Fusion）：在编码器层融合
   - 高层语义融合（Late Fusion）：在决策层融合

3. **自适应权重学习**：引入门控机制（Gating Mechanism）动态调整不同模态的贡献权重，公式为：w = σ(Wg·[h_v; h_t])，其中σ是sigmoid函数。

该方法在三个benchmark数据集上取得了显著提升：在VQA 2.0上accuracy从65.2%提升到71.8%，在COCO Caption上CIDEr分数从110.3提升到124.7。

**请开始回答当前子问题**："""


FAST_MODE_ANSWER_PROMPT = """你是一个专业的文档分析助手。当前处于快速模式，需要基于一次性召回的文档内容直接回答用户问题。

**用户问题**：
{user_query}

**召回的文档内容**：
{recalled_content}

**任务说明**：
请基于召回的文档内容，全面、准确地回答用户问题。

**回答要求**：
1. **全面覆盖**：尽可能覆盖用户问题涉及的所有方面
2. **结构化呈现**：使用清晰的结构组织内容（如标题、分点、编号等）
3. **保留关键信息**：重要数字、术语、公式、引用等必须保留
4. **逻辑连贯**：确保答案各部分之间逻辑通顺
5. **适度详细**：根据问题复杂度决定答案长度（通常500-2000字）

**输出格式**：
直接输出答案，使用markdown格式增强可读性。

**请开始回答**："""


def get_sub_question_context(qa_pairs: list) -> str:
    """
    Format previous QA pairs as context for current sub-question.
    
    Args:
        qa_pairs: List of QAPair dictionaries
        
    Returns:
        Formatted context string
    """
    if not qa_pairs:
        return "暂无（这是第一个子问题）"
    
    context_lines = []
    for i, qa in enumerate(qa_pairs, 1):
        context_lines.append(f"Q{i}: {qa['question']}")
        context_lines.append(f"A{i}: {qa['answer'][:200]}{'...' if len(qa['answer']) > 200 else ''}")
        context_lines.append("")
    
    return "\n".join(context_lines)


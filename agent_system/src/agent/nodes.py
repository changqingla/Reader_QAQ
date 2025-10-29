"""Node implementations for the agent graph."""
from typing import Dict, Any

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from .state import AgentState, IntentType, StepType, ExecutionResult, QAPair
from ..prompts import (
    INTENT_RECOGNITION_PROMPT,
    get_planning_prompt,
    TOOL_EXECUTION_PROMPT,
    INFORMATION_ANALYSIS_PROMPT,
    SIMPLE_INTERACTION_PROMPT,
    get_answer_prompt,
    SUB_QUESTION_ANSWER_PROMPT,
    get_sub_question_context
)
from ..utils.logger import get_logger
from ..utils.json_parser import parse_json_response
from ..tools import RecallTool, WebSearchTool
from config import get_settings

# 上下文管理模块 - 强制依赖
from context.session_manager import SessionManager
from context.session_storage import SessionStorage
from context.context_injector import ContextInjector

logger = get_logger(__name__)
settings = get_settings()


class AgentNodes:
    """Container for all agent node functions."""
    
    def __init__(
        self,
        llm: ChatOpenAI,
        recall_tool: RecallTool,
        web_search_tool: WebSearchTool = None
    ):
        """
        Initialize agent nodes.
        
        Args:
            llm: Language model for generation
            recall_tool: Tool for document retrieval
            web_search_tool: Optional tool for web search
        """
        self.llm = llm
        self.recall_tool = recall_tool
        self.web_search_tool = web_search_tool
        
        # 初始化上下文管理（强制依赖）
        storage = SessionStorage()
        self.session_manager = SessionManager(storage)
        self.context_injector = ContextInjector()
        
        logger.info("AgentNodes initialized with session management")
    
    def _execute_recall(
        self,
        query: str,
        state: AgentState
    ) -> str:
        """
        Execute recall with dynamic parameters from state.
        
        Args:
            query: Search query
            state: Agent state containing optional recall parameters
            
        Returns:
            Recall results
        """
        # Get dynamic parameters from state if provided
        index_names = state.get('recall_index_names')
        doc_ids = state.get('recall_doc_ids')
        
        # Call recall tool's _run method directly with optional parameters
        return self.recall_tool._run(
            query=query,
            index_names=index_names,
            doc_ids=doc_ids
        )
    
    def _get_conversation_context(
        self,
        state: AgentState,
        num_turns: int = 2,
        stage: str = "intent_recognition"
    ) -> str:
        """
        获取对话上下文
        
        Args:
            state: Agent state
            num_turns: 需要的对话轮次数（未使用，保留用于兼容）
            stage: 处理阶段（intent_recognition, planning, answer_generation）
            
        Returns:
            格式化的对话历史字符串
        """
        session_id = state.get('session_id')
        if not session_id:
            logger.warning("No session_id provided, cannot retrieve context")
            return ""
        
        # 根据阶段选择合适的注入方法
        if stage == "intent_recognition":
            messages = self.context_injector.inject_for_intent_recognition(session_id)
        elif stage == "planning":
            messages = self.context_injector.inject_for_planning(session_id)
        elif stage == "answer_generation":
            messages = self.context_injector.inject_for_answer_generation(session_id)
        elif stage == "simple_interaction":
            messages = self.context_injector.inject_for_simple_interaction(session_id)
        else:
            logger.warning(f"Unknown stage: {stage}")
            messages = []
        
        if not messages:
            return ""
        
        # 使用ContextInjector的格式化方法
        return self.context_injector.format_messages_for_prompt(messages)
    
    def _format_execution_history(self, execution_results: list) -> str:
        """
        Format execution history for replanning context.
        
        Args:
            execution_results: List of execution results
            
        Returns:
            Formatted execution history string
        """
        if not execution_results:
            return "无执行历史"
        
        history = []
        for r in execution_results:
            status = "✅ 成功" if not r.get('error') else f"❌ 失败: {r.get('error')}"
            tool = r.get('tool_used') or '无工具'
            query = r.get('query') or '无查询'
            result = r.get('result') or ''
            result_preview = result[:200] if result else '无结果'
            
            # 安全处理query切片
            query_str = str(query) if query else '无查询'
            query_preview = query_str[:150] + ('...' if len(query_str) > 150 else '')
            
            history.append(
                f"【步骤 {r['step_index']+1}】{r['step_title']} (类型: {r['step_type']})\n"
                f"  - 使用工具: {tool}\n"
                f"  - 查询内容: {query_preview}\n"
                f"  - 执行状态: {status}\n"
                f"  - 结果预览: {result_preview}{'...' if len(result_preview) >= 200 else ''}"
            )
        return "\n\n".join(history)
    
    def _build_replanning_context(self, state: AgentState, replan_count: int) -> str:
        """
        Build replanning context with execution history and analysis results.
        
        Args:
            state: Current agent state
            replan_count: Number of replanning attempts
            
        Returns:
            Formatted replanning context string
        """
        plan = state.get('plan', {})
        analysis = state.get('analysis_result', {})
        execution_results = state.get('execution_results', [])
        collected_info = state.get('collected_information', '')
        
        context_parts = [
            "=" * 80,
            f"🔄 重要提示：这是第 {replan_count} 次重新规划",
            "=" * 80,
            "",
            "【上一次规划的情况】",
            f"规划标题: {plan.get('title', '无')}",
            f"规划思路: {plan.get('thought', '无')[:200]}...",
            f"执行步骤数: {len(plan.get('steps', []))} 步",
            "",
            "【执行历史详情】",
            self._format_execution_history(execution_results),
            "",
            "【信息充分性分析】",
            f"分析结论: {analysis.get('analysis', '无分析结果')}",
            ""
        ]
        
        # 添加缺失方面
        missing_aspects = analysis.get('missing_aspects', [])
        if missing_aspects:
            context_parts.append("【❗ 缺失的关键信息】")
            for i, aspect in enumerate(missing_aspects, 1):
                context_parts.append(f"  {i}. {aspect}")
            context_parts.append("")
        
        # 添加建议行动
        suggested_actions = analysis.get('suggested_actions', [])
        if suggested_actions:
            context_parts.append("【💡 建议的补充行动】")
            for i, action in enumerate(suggested_actions, 1):
                context_parts.append(f"  {i}. {action}")
            context_parts.append("")
        
        # 添加已收集信息的摘要
        if collected_info and collected_info.strip():
            info_preview = collected_info[:500] + "..." if len(collected_info) > 500 else collected_info
            context_parts.extend([
                "【已收集的信息摘要】",
                info_preview,
                ""
            ])
        
        context_parts.extend([
            "=" * 80,
            "📝 重新规划指导：",
            "1. 分析上述执行历史，找出为什么信息不充分",
            "2. 重点关注「缺失的关键信息」和「建议的补充行动」",
            "3. 调整检索策略：",
            "   - 如果之前的查询词太宽泛，使用更具体的查询",
            "   - 如果之前的查询词太具体，尝试更宽泛的查询",
            "   - 如果某个方面完全没有检索，增加对应的recall步骤",
            "   - 考虑使用不同的检索角度或关键词",
            "4. 避免重复之前失败的策略",
            "5. 如果是文档内容问题，考虑用更明确的问法检索",
            "=" * 80,
            ""
        ])
        
        return "\n".join(context_parts)
    
    def intent_recognition_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Recognize user intent from query.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with detected intent
        """
        logger.info("============ Intent Recognition Node ============")
        logger.info(f"User query: {state['user_query'][:100]}...")
        logger.info(f"Previous messages: {len(state.get('messages', []))}")
        
        try:
            # Check if mode_type is provided
            if state.get("mode_type"):
                mode_type = state["mode_type"]
                logger.info(f"Using provided mode_type: {mode_type}")
                
                # Validate it's a valid IntentType
                try:
                    detected_intent = IntentType(mode_type)
                    logger.info(f"Validated intent: {detected_intent}")
                    return {
                        "detected_intent": detected_intent,
                        "messages": state.get("messages", []) + [
                            HumanMessage(content=state["user_query"])
                        ]
                    }
                except ValueError:
                    logger.warning(f"Invalid mode_type: {mode_type}, falling back to LLM")
            
            # Build context-aware prompt for intent recognition
            query_with_context = state["user_query"]
            
            # 获取对话历史上下文（2轮）
            context_str = self._get_conversation_context(state, num_turns=2, stage="intent_recognition")
            
            if context_str:
                query_with_context = f"对话历史：\n{context_str}\n\n当前问题：{state['user_query']}"
                logger.info("Using conversation history for intent recognition (2 turns)")
            
            # Use LLM to detect intent
            prompt = INTENT_RECOGNITION_PROMPT.format(user_query=query_with_context)
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse JSON response
            intent_data = parse_json_response(response.content, expected_fields=["intent"])
            
            if intent_data:
                intent_str = intent_data.get("intent")
                confidence = intent_data.get("confidence", "unknown")
                reasoning = intent_data.get("reasoning", "")
                
                # 显示大模型判断的任务类型
                logger.info("="*60)
                logger.info("🎯 大模型判断结果:")
                logger.info(f"   任务类型: {intent_str}")
                logger.info(f"   置信度: {confidence}")
                logger.info(f"   判断依据: {reasoning}")
                logger.info("="*60)
            else:
                # Fallback: try to extract intent from plain text
                intent_str = response.content.strip()
                logger.warning(f"Failed to parse JSON, trying plain text: {intent_str}")
            
            try:
                detected_intent = IntentType(intent_str)
            except ValueError:
                logger.warning(f"Invalid intent from LLM: {intent_str}, defaulting to knowledge_reasoning")
                detected_intent = IntentType.KNOWLEDGE_REASONING
            
            return {
                "detected_intent": detected_intent,
                "messages": state.get("messages", []) + [
                    HumanMessage(content=state["user_query"])
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in intent recognition: {str(e)}", exc_info=True)
            raise RuntimeError(f"Intent recognition failed: {str(e)}")
    
    def simple_interaction_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Handle simple interactions directly.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with final answer
        """
        logger.info("============ Simple Interaction Node ============")
        
        try:
            # 🔑 关键修复：注入对话历史，让Agent能记住之前的对话
            query_with_context = state["user_query"]
            
            # 获取对话历史上下文（最近2轮对话）
            context_str = self._get_conversation_context(state, num_turns=0, stage="simple_interaction")
            
            if context_str:
                query_with_context = f"【对话历史】\n{context_str}\n\n【当前问题】\n{state['user_query']}"
                logger.info("✅ Simple interaction using ALL active conversation history (with token limit protection)")
            else:
                logger.info("⚠️  No conversation history available")
            
            prompt = SIMPLE_INTERACTION_PROMPT.format(user_query=query_with_context)
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            final_answer = response.content
            logger.info(f"Generated simple response: {final_answer[:100]}...")
            
            # 会话管理：保存消息（simple_interaction跳过了planning/execution）
            session_id = state.get('session_id')
            if session_id:
                # 🔑 关键：保存用户消息（在workflow结束时保存，而不是开始时）
                if not state.get('_user_message_saved'):
                    self.session_manager.add_user_message(
                        session_id=session_id,
                        content=state["user_query"]
                    )
                    logger.info(f"User message saved to session {session_id}")
                
                # 保存助手回复
                self.session_manager.add_assistant_message(
                    session_id=session_id,
                    content=final_answer
                )
                logger.info(f"✅ Assistant message saved to session {session_id}")
                
                # 检查是否需要压缩
                if self.session_manager.should_compress(session_id):
                    logger.info(f"Triggering compression for session {session_id}")
                    compression_record = self.session_manager.trigger_compression(session_id)
                    logger.info(
                        f"Compression completed: saved {compression_record.saved_tokens} tokens, "
                        f"round {compression_record.round}"
                    )
            
            return {
                "final_answer": final_answer,
                "messages": state.get("messages", []) + [
                    AIMessage(content=final_answer)
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in simple interaction: {str(e)}", exc_info=True)
            raise RuntimeError(f"Simple interaction failed: {str(e)}")
    
    def plan_generation_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Generate execution plan based on intent.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with execution plan
        """
        replan_count = state.get("replan_count", 0)
        
        logger.info("================ Plan Generation Node ================")
        logger.info(f"Intent: {state['detected_intent']}")
        logger.info(f"Replan count: {replan_count}")
        
        deep_thinking = state.get("deep_thinking", False)
        logger.info(f"Planning mode: {'Deep Thinking' if deep_thinking else 'Fast'}")
        
        try:
            # Build context-aware query
            query_with_context = state["user_query"]
            
            # 获取对话历史上下文（2轮）
            context_str = self._get_conversation_context(state, num_turns=2, stage="planning")
            
            if context_str:
                query_with_context = f"对话历史（用于理解代词和上下文）：\n{context_str}\n\n当前问题：{state['user_query']}"
                logger.info("Using conversation history for planning (2 turns)")
            
            # 🔑 关键优化：如果是重新规划，添加执行历史和分析结果
            if replan_count > 0:
                replanning_context = self._build_replanning_context(state, replan_count)
                query_with_context = f"{replanning_context}\n\n{query_with_context}"
                logger.info(f"Added replanning context (attempt {replan_count})")
                logger.info("=" * 60)
                logger.info("🔄 Replanning Context Preview:")
                logger.info(replanning_context[:500] + "...")
                logger.info("=" * 60)
            
            # Get the appropriate planning prompt based on intent and mode
            prompt_template = get_planning_prompt(
                intent_type=state["detected_intent"],
                deep_thinking=deep_thinking
            )
            
            # Format prompt with user query
            prompt = prompt_template.format(user_query=query_with_context)
            
            # Generate plan
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Parse JSON response
            plan = parse_json_response(
                response.content,
                expected_fields=["locale", "thought", "title", "steps"]
            )
            
            if not plan:
                raise ValueError("Failed to parse plan JSON from LLM response")
            
            # logger.info(f"Generated plan: {plan}")
            # logger.info(f"Generated plan: {plan['title']}")
            # logger.info(f"Number of steps: {len(plan['steps'])}")
            
            # Print complete plan details
            logger.info("=" * 60)
            logger.info("📋 完整任务规划")
            logger.info("=" * 60)
            logger.info(f"标题: {plan['title']}")
            logger.info(f"\n思考过程:\n{plan['thought']}")
            logger.info(f"\n执行步骤 (共{len(plan['steps'])}步):")
            for i, step in enumerate(plan['steps'], 1):
                logger.info(f"步骤 {i}. [{step['step_type']}] {step['title']}")
            logger.info("=" * 60)
            
            # 🔑 关键修复：重新规划时保留之前收集的信息
            # 只重置当前规划的执行状态，不清空已收集的信息
            if replan_count > 0:
                # 重新规划：保留已收集的信息和执行历史
                logger.info("🔄 保存之前的执行结果和收集的信息")
                return {
                    "plan": plan,
                    "current_step_index": 0,
                    # 保留之前的执行结果（用于历史记录）
                    "execution_results": state.get("execution_results", []),
                    # 保留之前收集的信息（累积）
                    "collected_information": state.get("collected_information", "")
                }
            else:
                # 首次规划：初始化为空
                return {
                    "plan": plan,
                    "current_step_index": 0,
                    "execution_results": [],
                    "collected_information": ""
                }
            
        except Exception as e:
            logger.error(f"Error in plan generation: {str(e)}", exc_info=True)
            raise RuntimeError(f"Plan generation failed: {str(e)}")
    
    def execution_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute current step in the plan.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with execution results
        """
        plan = state["plan"]
        current_step_index = state["current_step_index"]
        current_step = plan["steps"][current_step_index]
        
        logger.info(f"============ Execution Node - Step {current_step_index + 1}/{len(plan['steps'])} ============")
        logger.info(f"Step title: {current_step['title']}")
        logger.info(f"Step type: {current_step['step_type']}")
        
        try:
            # Build context-aware user query
            # 注意：execution阶段配置为不注入历史（execution_turns=0）
            # 因为工具执行主要基于当前步骤的明确指令，不需要完整对话历史
            user_query_with_context = state["user_query"]
            
            # Prepare tool execution prompt
            use_direct_content = state.get("use_direct_content", False)
            
            # 🔑 优化：在直接内容模式下，明确告知 LLM
            collected_info = state.get("collected_information", "暂无")
            if use_direct_content and collected_info != "暂无":
                collected_info = f"📄 **已提供完整文档内容**（直接内容模式，无需再次 recall）\n\n{collected_info}"
            
            prompt = TOOL_EXECUTION_PROMPT.format(
                user_query=user_query_with_context,
                step_title=current_step["title"],
                step_type=current_step["step_type"],
                step_index=current_step_index + 1,
                total_steps=len(plan["steps"]),
                collected_information=collected_info,
                web_search_available="可用" if state.get("enable_web_search") and self.web_search_tool else "不可用"
            )
            
            # Get tool decision
            response = self.llm.invoke([HumanMessage(content=prompt)])
            decision = parse_json_response(
                response.content,
                expected_fields=["need_tool"]  # Only require need_tool field
            )
            
            if not decision:
                logger.error(f"Failed to parse tool decision. Response: {response.content[:500]}")
                # Fallback: default behavior based on step type
                if current_step["step_type"] == "recall":
                    # For recall steps, default to calling recall tool
                    decision = {
                        "need_tool": True,
                        "tool_name": "recall",
                        "query": f"{state['user_query']} - {current_step['title']}",
                        "reasoning": "Fallback: Auto-generated query for recall step"
                    }
                    logger.warning("Using fallback decision for recall step")
                else:
                    # For other steps, skip tool if we can't parse decision
                    decision = {
                        "need_tool": False,
                        "tool_name": None,
                        "query": None,
                        "reasoning": "Fallback: Skipping tool due to parse error"
                    }
                    logger.warning("Using fallback decision: skipping tool")
            
            logger.info(f"Tool decision: {decision['reasoning']}")
            
            # 🔑 Check if direct content mode is enabled for recall steps
            use_direct_content = state.get("use_direct_content", False)
            direct_content = state.get("direct_content")
            
            if use_direct_content and current_step["step_type"] == "recall":
                logger.info("=" * 60)
                logger.info("📄 直接内容模式：跳过 recall 工具，使用提供的文档内容")
                logger.info(f"   内容长度: {len(direct_content):,} 字符")
                logger.info(f"   Token 数: {state.get('content_token_count', 'N/A')}")
                logger.info("=" * 60)
                
                # Create execution result with direct content
                execution_result: ExecutionResult = {
                    "step_index": current_step_index,
                    "step_title": current_step["title"],
                    "step_type": StepType.RECALL,
                    "tool_used": "direct_content",
                    "query": "使用用户提供的完整文档内容",
                    "result": direct_content,
                    "error": None
                }
                
                # Skip normal tool execution, go directly to result handling
                # (continue with the existing code below)
            else:
                # Prepare execution result for normal tool execution
                execution_result: ExecutionResult = {
                    "step_index": current_step_index,
                    "step_title": current_step["title"],
                    "step_type": StepType(current_step["step_type"]),
                    "tool_used": decision.get("tool_name"),
                    "query": decision.get("query"),
                    "result": "",
                    "error": None
                }
            
            # Execute tool if needed (only when not using direct content)
            if not (use_direct_content and current_step["step_type"] == "recall") and decision["need_tool"] and decision.get("tool_name"):
                tool_name = decision["tool_name"]
                query = decision["query"]
                
                logger.info(f"Calling tool: {tool_name} with query: {query[:200]}...")
                
                try:
                    if tool_name == "recall":
                        tool_result = self._execute_recall(query, state)
                    elif tool_name == "web_search":
                        if not self.web_search_tool:
                            raise RuntimeError("Web search tool is not available")
                        tool_result = self.web_search_tool.run(query)
                    else:
                        raise ValueError(f"Unknown tool: {tool_name}")
                    
                    execution_result["result"] = tool_result
                    logger.info(f"Tool execution successful, result length: {len(tool_result)}")
                    
                except Exception as tool_error:
                    error_msg = f"Tool execution error: {str(tool_error)}"
                    logger.error(error_msg, exc_info=True)
                    execution_result["error"] = error_msg
                    execution_result["result"] = f"工具调用失败: {str(tool_error)}"
                    
            else:
                # 🔑 修复：如果是直接内容模式，result 已经被设置为完整文档，不要覆盖
                if not (use_direct_content and current_step["step_type"] == "recall"):
                    execution_result["result"] = f"无需工具调用: {decision['reasoning']}"
                logger.info("No tool execution needed")
            
            # Update state - different logic for deep thinking mode
            updated_results = state.get("execution_results", []) + [execution_result]
            
            # Check if deep thinking mode is enabled
            deep_thinking = state.get("deep_thinking", False)
            
            if deep_thinking and current_step["step_type"] == "recall":
                # Deep thinking mode: generate QA pair for recall steps
                logger.info("Deep thinking mode: Generating QA pair for this step")
                
                try:
                    # Get previous QA pairs for context
                    previous_qa_pairs = state.get("qa_pairs", [])
                    previous_context = get_sub_question_context(previous_qa_pairs)
                    
                    # Prepare sub-question answer prompt
                    sub_question = current_step["title"]
                    recalled_content = execution_result["result"] if execution_result["result"] else "（未召回到相关内容）"
                    
                    prompt = SUB_QUESTION_ANSWER_PROMPT.format(
                        user_query=user_query_with_context,
                        step_index=current_step_index + 1,
                        total_steps=len(plan["steps"]),
                        sub_question=sub_question,
                        previous_qa_context=previous_context,
                        recalled_content=recalled_content
                    )
                    
                    # Generate answer for this sub-question
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    sub_answer = response.content
                    
                    logger.info(f"Generated sub-answer, length: {len(sub_answer)} characters")
                    
                    # Create QA pair
                    qa_pair: QAPair = {
                        "step_index": current_step_index,
                        "question": sub_question,
                        "answer": sub_answer,
                        "recall_query": decision.get("query")
                    }
                    
                    updated_qa_pairs = previous_qa_pairs + [qa_pair]
                    
                    return {
                        "execution_results": updated_results,
                        "qa_pairs": updated_qa_pairs,
                        "current_step_index": current_step_index + 1
                    }
                    
                except Exception as e:
                    logger.error(f"Error generating QA pair: {str(e)}", exc_info=True)
                    # Fallback: treat as fast mode
                    logger.warning("Falling back to fast mode due to QA generation error")
                    deep_thinking = False
            
            # Fast mode or non-recall steps: accumulate information
            if not deep_thinking:
                updated_info = state.get("collected_information", "")
                if execution_result["result"] and not execution_result.get("error"):
                    updated_info += f"\n\n【步骤 {current_step_index + 1}: {current_step['title']}】\n{execution_result['result']}"
                
                return {
                    "execution_results": updated_results,
                    "collected_information": updated_info,
                    "current_step_index": current_step_index + 1
                }
            else:
                # Deep thinking mode but non-recall step (analysis/synthesis)
                # Just move to next step without generating QA
                return {
                    "execution_results": updated_results,
                    "current_step_index": current_step_index + 1
                }
            
        except Exception as e:
            logger.error(f"Error in execution node: {str(e)}", exc_info=True)
            # Record error but continue
            error_result: ExecutionResult = {
                "step_index": current_step_index,
                "step_title": current_step["title"],
                "step_type": StepType(current_step["step_type"]),
                "tool_used": None,
                "query": None,
                "result": "",
                "error": str(e)
            }
            return {
                "execution_results": state.get("execution_results", []) + [error_result],
                "current_step_index": current_step_index + 1,
                "error": str(e)
            }
    
    def analysis_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Analyze if collected information is sufficient.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with analysis results
        """
        logger.info("============ Analysis Node ============")
        
        try:
            # Build execution summary
            execution_summary = "\n".join([
                f"步骤{r['step_index']+1}: {r['step_title']} - 工具: {r.get('tool_used', '无')}"
                for r in state.get("execution_results", [])
            ])
            
            # Prepare analysis prompt
            prompt = INFORMATION_ANALYSIS_PROMPT.format(
                user_query=state["user_query"],
                task_type=state["detected_intent"].value,
                collected_information=state.get("collected_information", ""),
                execution_summary=execution_summary
            )
            
            # Get analysis
            response = self.llm.invoke([HumanMessage(content=prompt)])
            analysis = parse_json_response(
                response.content,
                expected_fields=["is_sufficient", "analysis"]
            )
            
            if not analysis:
                logger.warning("Failed to parse analysis JSON, defaulting to sufficient")
                analysis = {
                    "is_sufficient": True,
                    "analysis": "无法解析分析结果，继续生成答案",
                    "missing_aspects": [],
                    "suggested_actions": []
                }
            
            is_sufficient = analysis["is_sufficient"]
            logger.info(f"Information sufficient: {is_sufficient}")
            logger.info(f"Analysis: {analysis['analysis'][:200]}...")
            
            # Check replan count
            replan_count = state.get("replan_count", 0)
            if not is_sufficient:
                if replan_count >= settings.max_replan_attempts:
                    logger.warning(f"Max replan attempts ({settings.max_replan_attempts}) reached, proceeding with available information")
                    is_sufficient = True
                    analysis["analysis"] += "\n（已达最大重新规划次数，将基于现有信息生成答案）"
                else:
                    # Increment replan counter
                    replan_count += 1
                    logger.info(f"Information insufficient, replanning (attempt {replan_count}/{settings.max_replan_attempts})")
            
            return {
                "is_information_sufficient": is_sufficient,
                "analysis_result": analysis,
                "replan_count": replan_count
            }
            
        except Exception as e:
            logger.error(f"Error in analysis node: {str(e)}", exc_info=True)
            # Default to sufficient to avoid infinite loops
            return {
                "is_information_sufficient": True,
                "analysis_result": {
                    "is_sufficient": True,
                    "analysis": f"分析过程出错: {str(e)}，将基于现有信息生成答案",
                    "missing_aspects": [],
                    "suggested_actions": []
                },
                "error": str(e)
            }
    
    def answer_generation_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Generate final answer based on collected information or QA pairs.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with final answer
        """
        logger.info("============ Answer Generation Node ============")
        logger.info(f"Intent: {state['detected_intent']}")
        
        deep_thinking = state.get("deep_thinking", False)
        logger.info(f"Mode: {'Deep Thinking' if deep_thinking else 'Fast'}")
        
        try:
            # Build context-aware query for answer generation
            user_query_with_context = state["user_query"]
            
            # 获取对话历史上下文（3轮 - answer generation需要更多上下文）
            context_str = self._get_conversation_context(state, num_turns=3, stage="answer_generation")
            
            if context_str:
                user_query_with_context = f"【对话历史（用于理解上下文和代词）】\n{context_str}\n\n【当前问题】\n{state['user_query']}"
                logger.info("Using conversation history for answer generation (3 turns)")
            
            # Prepare context based on mode
            if deep_thinking:
                # Deep thinking mode: use QA pairs
                qa_pairs = state.get("qa_pairs", [])
                logger.info(f"Using {len(qa_pairs)} QA pairs for answer generation")
                
                # Format QA pairs as context
                if qa_pairs:
                    qa_context_lines = []
                    for i, qa in enumerate(qa_pairs, 1):
                        qa_context_lines.append(f"## 子问题 {i}: {qa['question']}\n")
                        qa_context_lines.append(f"{qa['answer']}\n")
                    context_for_llm = "\n".join(qa_context_lines)
                else:
                    context_for_llm = "（没有生成QA对，可能所有步骤都是analysis/synthesis类型）"
                    logger.warning("No QA pairs found in deep thinking mode")
            else:
                # Fast mode: use collected information
                context_for_llm = state.get("collected_information", "")
                logger.info(f"Using collected information, length: {len(context_for_llm)} chars")
            
            # Get the appropriate answer prompt
            prompt_template = get_answer_prompt(state["detected_intent"])
            prompt = prompt_template.format(
                user_query=user_query_with_context,
                collected_information=context_for_llm
            )
            
            # Generate answer
            response = self.llm.invoke([HumanMessage(content=prompt)])
            final_answer = response.content
            
            logger.info(f"Generated answer length: {len(final_answer)} characters")
            
            # Log QA pairs summary if in deep thinking mode
            if deep_thinking and qa_pairs:
                logger.info("=" * 60)
                logger.info("📊 深度思考模式 - QA对总结")
                logger.info("=" * 60)
                for i, qa in enumerate(qa_pairs, 1):
                    logger.info(f"Q{i}: {qa['question']}")
                    answer_preview = qa['answer'][:150] + "..." if len(qa['answer']) > 150 else qa['answer']
                    logger.info(f"A{i}: {answer_preview}")
                    logger.info("-" * 60)
            
            # ========================================================================
            # 会话管理：保存消息和检查压缩
            # ========================================================================
            session_id = state.get('session_id')
            if session_id:
                # 🔑 关键：保存用户消息（在workflow结束时保存，而不是开始时）
                # 这样确保context injection时不会包含当前的user消息，避免重复
                if not state.get('_user_message_saved'):
                    self.session_manager.add_user_message(
                        session_id=session_id,
                        content=state["user_query"]
                    )
                    logger.info(f"User message saved to session {session_id}")
                
                # 保存助手回复
                self.session_manager.add_assistant_message(
                    session_id=session_id,
                    content=final_answer
                )
                logger.debug(f"Assistant message saved to session {session_id}")
                
                # 检查是否需要压缩
                if self.session_manager.should_compress(session_id):
                    logger.info(f"Triggering compression for session {session_id}")
                    compression_record = self.session_manager.trigger_compression(session_id)
                    logger.info(
                        f"Compression completed: saved {compression_record.saved_tokens} tokens, "
                        f"round {compression_record.round}"
                    )
            
            return {
                "final_answer": final_answer,
                "messages": state.get("messages", []) + [
                    AIMessage(content=final_answer)
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in answer generation: {str(e)}", exc_info=True)
            raise RuntimeError(f"Answer generation failed: {str(e)}")


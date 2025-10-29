# 修改说明：动态 Recall 参数支持

## 修改概述

将原本在环境变量中硬编码的 `RECALL_INDEX_NAMES` 和 `RECALL_DOC_IDS` 参数改为可由用户在每次请求时动态传入。

## 修改的文件

### 1. `api.py`

**修改内容**：
- 在 `QueryRequest` 模型中添加两个可选字段：
  - `recall_index_names: Optional[list]` - Recall 索引名称列表
  - `recall_doc_ids: Optional[list]` - Recall 文档ID列表
- 在 `process_query` 调用中传递这两个参数

**代码位置**：第 89-97 行，第 191-192 行

### 2. `src/agent/agent.py`

**修改内容**：
- 在 `process_query` 方法签名中添加两个参数：
  - `recall_index_names: Optional[List[str]] = None`
  - `recall_doc_ids: Optional[List[str]] = None`
- 在 docstring 中添加参数说明
- 在 `initial_state` 中添加这两个字段，传递给 workflow

**代码位置**：第 103-104 行，第 117-118 行，第 257-258 行

### 3. `src/agent/state.py`

**修改内容**：
- 在 `AgentState` TypedDict 中添加两个字段：
  - `recall_index_names: Optional[List[str]]` - 动态覆盖的索引名称
  - `recall_doc_ids: Optional[List[str]]` - 动态覆盖的文档ID

**代码位置**：第 128-130 行

### 4. `src/tools/recall_tool.py`

**修改内容**：
- 在 `RecallTool._run` 方法中添加两个可选参数：
  - `index_names: Optional[List[str]] = None`
  - `doc_ids: Optional[List[str]] = None`
- 在方法内部使用这些参数覆盖实例默认值：
  - `final_index_names = index_names if index_names is not None else self.index_names`
  - `final_doc_ids = doc_ids if doc_ids is not None else self.doc_ids`
- 添加日志输出，显示实际使用的参数

**代码位置**：第 62-63 行，第 79-85 行

### 5. `src/agent/nodes.py`

**修改内容**：
- 添加新方法 `_execute_recall(query, state)`:
  - 从 state 中提取 `recall_index_names` 和 `recall_doc_ids`
  - 调用 `self.recall_tool._run()` 并传递这些参数
- 修改 `execution_node` 中的 recall 调用：
  - 将 `self.recall_tool.run(query)` 改为 `self._execute_recall(query, state)`

**代码位置**：第 60-84 行，第 611 行

### 6. `README.md`

**修改内容**：
- 在请求 Body 示例中添加新参数
- 在字段说明表格中添加两个新字段的说明
- 添加示例4，展示如何使用这两个参数

**代码位置**：第 18-19 行，第 34-35 行，第 157-188 行

### 7. 新增文件

**`example_usage.md`**：
- 详细的使用示例文档
- 包含 curl 和 Python 示例
- 说明优势和注意事项

## 工作原理

1. **用户请求** → API 接收 `recall_index_names` 和 `recall_doc_ids`
2. **agent.process_query** → 将参数添加到 `AgentState`
3. **workflow 执行** → state 在各个节点间传递
4. **execution_node** → 当需要执行 recall 时调用 `_execute_recall`
5. **_execute_recall** → 从 state 提取参数，传递给 `recall_tool._run()`
6. **recall_tool._run** → 使用传入的参数覆盖默认值，发送 API 请求

## 向后兼容性

- ✅ 不传这两个参数时，使用环境变量中的默认配置
- ✅ 现有代码无需修改即可继续工作
- ✅ 可以逐步迁移到动态参数模式

## 测试建议

### 测试场景1：不传参数（使用默认配置）
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"user_query": "测试问题"}'
```
**期望**：使用环境变量中的 `RECALL_INDEX_NAMES` 和 `RECALL_DOC_IDS`

### 测试场景2：只传 index_names
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "测试问题",
    "recall_index_names": ["custom_index"]
  }'
```
**期望**：使用 `custom_index`，doc_ids 使用环境变量默认值

### 测试场景3：同时传 index_names 和 doc_ids
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "测试问题",
    "recall_index_names": ["index1", "index2"],
    "recall_doc_ids": ["doc1", "doc2", "doc3"]
  }'
```
**期望**：使用指定的索引和文档ID

### 测试场景4：多轮对话
```bash
# 第一轮
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "第一个问题",
    "session_id": "test-session",
    "recall_index_names": ["docs"]
  }'

# 第二轮（相同session）
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "继续问",
    "session_id": "test-session",
    "recall_index_names": ["docs"]
  }'
```
**期望**：每轮使用各自指定的参数，会话历史正常保持

## 日志验证

修改后，在日志中可以看到：
```
INFO - Executing recall with query: 用户问题...
INFO - Using index_names: ['custom_index']
INFO - Using doc_ids: ['doc1', 'doc2']
```

## 环境变量配置（可选）

如果想设置默认值，在 `.env` 文件中配置：
```bash
# Recall 配置（默认值，可被 API 参数覆盖）
RECALL_INDEX_NAMES=deeprag_vectors,backup_index
RECALL_DOC_IDS=  # 留空表示不限制文档
```

## 总结

此次修改实现了：
- ✅ 用户可以在每次请求时指定检索范围
- ✅ 保持向后兼容，不传参数时使用默认配置
- ✅ 代码结构清晰，易于维护
- ✅ 支持多租户场景，不同用户检索不同文档集合
- ✅ 提高检索效率，通过限定范围减少检索时间

修改完成！🎉


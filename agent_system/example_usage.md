# 使用示例：动态 Recall 参数

本文档展示如何使用新添加的 `recall_index_names` 和 `recall_doc_ids` 参数。

## 功能说明

之前这两个参数是在环境变量 `.env` 文件中硬编码的：
- `RECALL_INDEX_NAMES`: 指定要检索的索引名称列表
- `RECALL_DOC_IDS`: 指定要检索的文档ID列表（可选）

现在这两个参数可以在每次请求时由用户动态传入，覆盖环境变量的默认配置。

## 使用方法

### 1. 使用默认配置（不传参数）

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "什么是量子计算？"
  }'
```

这种情况下，系统会使用环境变量中配置的默认索引和文档ID。

### 2. 指定特定索引

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "产品A的技术规格是什么？",
    "recall_index_names": ["product_docs", "technical_specs"]
  }'
```

这会只在 `product_docs` 和 `technical_specs` 两个索引中检索。

### 3. 指定特定文档ID

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "这个文档的摘要是什么？",
    "recall_index_names": ["company_docs"],
    "recall_doc_ids": ["doc_2024_Q1_report", "doc_2024_Q2_report"]
  }'
```

这会只在指定的两个文档中检索信息。

### 4. 结合会话使用

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_query": "对比这两个产品的性能",
    "session_id": "my-session-123",
    "recall_index_names": ["product_comparison"],
    "recall_doc_ids": ["product_A", "product_B"]
  }'
```

## Python 示例

```python
import requests

# API 端点
url = "http://localhost:8000/query"

# 示例1：使用默认配置
response = requests.post(url, json={
    "user_query": "什么是机器学习？"
})
print(response.json())

# 示例2：指定索引和文档
response = requests.post(url, json={
    "user_query": "产品的价格是多少？",
    "recall_index_names": ["product_catalog"],
    "recall_doc_ids": ["product_A_pricing", "product_B_pricing"]
})
print(response.json())

# 示例3：多轮对话 + 自定义检索
session_id = "user-123-session"
response = requests.post(url, json={
    "user_query": "帮我总结这些文档",
    "session_id": session_id,
    "recall_index_names": ["legal_docs"],
    "recall_doc_ids": ["contract_2024_001", "contract_2024_002"]
})
print(response.json())

# 继续对话
response = requests.post(url, json={
    "user_query": "有什么风险点吗？",
    "session_id": session_id,  # 使用相同的 session_id
    "recall_index_names": ["legal_docs"],  # 保持相同的检索范围
    "recall_doc_ids": ["contract_2024_001", "contract_2024_002"]
})
print(response.json())
```

## 优势

1. **灵活性**: 不同的查询可以检索不同的索引和文档
2. **性能**: 通过限定检索范围，提高检索速度和准确性
3. **隔离性**: 多租户场景下，每个用户可以检索自己的文档集合
4. **兼容性**: 不传参数时使用默认配置，向后兼容

## 实现细节

修改涉及以下文件：

1. **api.py**: 在 `QueryRequest` 中添加 `recall_index_names` 和 `recall_doc_ids` 字段
2. **agent.py**: 在 `process_query` 方法中接收并传递这两个参数到状态
3. **state.py**: 在 `AgentState` 中添加这两个字段
4. **recall_tool.py**: 修改 `_run` 方法支持动态参数覆盖
5. **nodes.py**: 添加 `_execute_recall` 方法，从状态中获取参数并调用 recall

## 注意事项

- 参数类型为 `array[string]`，即字符串数组
- 如果不传这两个参数，系统会使用环境变量中的默认配置
- 如果传入空数组 `[]`，可能导致检索失败，建议传入 `null` 或不传
- 这两个参数只影响 recall 工具，不影响 web_search 等其他工具


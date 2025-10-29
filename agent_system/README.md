# API 接口文档

## 1. 查询处理

**接口**: `POST /query`

### 请求 Body

```json
{
  "user_query": "string (必填)",
  "session_id": "string (可选)",
  "mode_type": "string (可选)",
  "enable_web_search": true,
  "deep_thinking": false,
  "content": "string (可选)",
  "force_recall": false,
  "recall_index_names": ["index1", "index2"],
  "recall_doc_ids": ["doc1", "doc2"]
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_query` | string | ✅ | 用户问题（1-10000字符） |
| `session_id` | string | ❌ | 会话ID。不传则自动生成新会话；传入已存在的ID则继续该会话 |
| `mode_type` | string | ❌ | 任务类型（simple_interaction, comparison_evaluation等） |
| `enable_web_search` | boolean | ❌ | 是否启用网页搜索 |
| `deep_thinking` | boolean | ❌ | 是否启用深度思考模式，默认false |
| `content` | string | ❌ | 完整文档内容。系统会**自动计算**当前可用tokens并判断是否直接使用 |
| `force_recall` | boolean | ❌ | 强制使用召回模式，默认false |
| `recall_index_names` | array[string] | ❌ | Recall检索的索引名列表。不传则使用环境变量配置 |
| `recall_doc_ids` | array[string] | ❌ | Recall检索的文档ID列表。不传则使用环境变量配置 |

### 返回格式

```json
{
  "success": true,
  "session_id": "uuid-xxx-xxx",
  "detected_intent": "QUESTION_ANSWERING",
  "plan": {...},
  "final_answer": "这是回答内容...",
  "execution_time": 3.14,
  "error": null,
  "session_total_tokens": 15000,
  "session_message_count": 10,
  "compression_threshold": 102400,
  "tokens_until_compression": 87400
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 是否成功处理 |
| `session_id` | string | 会话ID（用于后续对话） |
| `detected_intent` | string | 检测到的意图类型 |
| `plan` | object | 执行计划（如果有） |
| `final_answer` | string | 最终回答 |
| `execution_time` | float | 执行耗时（秒） |
| `error` | string | 错误信息（如果有） |
| `session_total_tokens` | integer | **会话已使用的总token数** |
| `session_message_count` | integer | **会话消息总数** |
| `compression_threshold` | integer | **触发压缩的阈值（102,400）** |
| `tokens_until_compression` | integer | **距离压缩还剩多少token** |

### 示例

#### 示例1：首次对话

**请求**：
```json
{
  "user_query": "什么是量子计算？"
}
```

**返回**：
```json
{
  "success": true,
  "session_id": "d4f2e8c1-3a5b-4d6e-8f7a-9b2c1d3e4f5a",
  "detected_intent": "QUESTION_ANSWERING",
  "plan": null,
  "final_answer": "量子计算是一种利用量子力学原理进行信息处理的计算方式...",
  "execution_time": 2.45,
  "error": null,
  "session_total_tokens": 350,
  "session_message_count": 2,
  "compression_threshold": 102400,
  "tokens_until_compression": 102050
}
```

#### 示例2：继续对话

**请求**：
```json
{
  "user_query": "它有哪些应用？",
  "session_id": "d4f2e8c1-3a5b-4d6e-8f7a-9b2c1d3e4f5a"
}
```

**返回**：
```json
{
  "success": true,
  "session_id": "d4f2e8c1-3a5b-4d6e-8f7a-9b2c1d3e4f5a",
  "detected_intent": "SIMPLE_INTERACTION",
  "plan": null,
  "final_answer": "量子计算的主要应用包括：\n1. 密码学...\n2. 药物研发...",
  "execution_time": 1.82,
  "error": null,
  "session_total_tokens": 680,
  "session_message_count": 4,
  "compression_threshold": 102400,
  "tokens_until_compression": 101720
}
```

#### 示例3：接近压缩阈值

**请求**：
```json
{
  "user_query": "详细解释一下量子纠缠",
  "session_id": "d4f2e8c1-3a5b-4d6e-8f7a-9b2c1d3e4f5a"
}
```

**返回**：
```json
{
  "success": true,
  "session_id": "d4f2e8c1-3a5b-4d6e-8f7a-9b2c1d3e4f5a",
  "detected_intent": "QUESTION_ANSWERING",
  "plan": {...},
  "final_answer": "量子纠缠是量子力学中最神奇的现象之一...",
  "execution_time": 4.21,
  "error": null,
  "session_total_tokens": 98500,
  "session_message_count": 20,
  "compression_threshold": 102400,
  "tokens_until_compression": 3900
}
```

**说明**：
- `tokens_until_compression` 接近0，表示即将触发压缩
- 下一次查询后可能会自动压缩历史消息

#### 示例4：指定特定索引和文档进行召回

**请求**：
```json
{
  "user_query": "这个产品的技术规格是什么？",
  "recall_index_names": ["product_docs"],
  "recall_doc_ids": ["product_A_spec", "product_A_manual"]
}
```

**返回**：
```json
{
  "success": true,
  "session_id": "auto-generated-uuid",
  "detected_intent": "QUESTION_ANSWERING",
  "plan": {...},
  "final_answer": "根据技术规格文档，该产品的主要技术参数包括...",
  "execution_time": 2.13,
  "error": null,
  "session_total_tokens": 420,
  "session_message_count": 2,
  "compression_threshold": 102400,
  "tokens_until_compression": 101980
}
```

**说明**：
- `recall_index_names` 指定只在 `product_docs` 索引中搜索
- `recall_doc_ids` 进一步限定只检索这两个特定文档
- 不传这两个参数时，使用环境变量中配置的默认值

#### 示例5：使用自定义session_id

**请求**：
```json
{
  "user_query": "你好",
  "session_id": "user123-chat-2024-01-27"
}
```

**返回**：
```json
{
  "success": true,
  "session_id": "user123-chat-2024-01-27",
  "detected_intent": "SIMPLE_INTERACTION",
  "plan": null,
  "final_answer": "你好！我是智能助手，有什么可以帮你的吗？",
  "execution_time": 0.56,
  "error": null,
  "session_total_tokens": 50,
  "session_message_count": 2,
  "compression_threshold": 102400,
  "tokens_until_compression": 102350
}
```

---

## 2. 获取会话历史

**接口**: `GET /conversation/{session_id}`

### URL参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `session_id` | string | 会话ID |

### 返回格式

```json
{
  "session_id": "uuid-xxx-xxx",
  "message_count": 4,
  "messages": [
    {
      "type": "HumanMessage",
      "content": "用户消息内容"
    },
    {
      "type": "AIMessage", 
      "content": "AI回复内容"
    }
  ]
}
```

### 示例

**请求**：
```
GET /conversation/d4f2e8c1-3a5b-4d6e-8f7a-9b2c1d3e4f5a
```

**返回**：
```json
{
  "session_id": "d4f2e8c1-3a5b-4d6e-8f7a-9b2c1d3e4f5a",
  "message_count": 4,
  "messages": [
    {
      "type": "HumanMessage",
      "content": "什么是量子计算？"
    },
    {
      "type": "AIMessage",
      "content": "量子计算是..."
    },
    {
      "type": "HumanMessage",
      "content": "它有哪些应用？"
    },
    {
      "type": "AIMessage",
      "content": "主要应用包括..."
    }
  ]
}
```

---

## 3. 健康检查

**接口**: `GET /health`

### 返回格式

```json
{
  "status": "healthy",
  "agent_ready": true
}
```

---

## 4. 根路径

**接口**: `GET /`

### 返回格式

```json
{
  "service": "Intelligent Agent API",
  "version": "1.0.0",
  "status": "running"
}
```

---

## 错误响应

### 格式

```json
{
  "detail": "错误描述信息"
}
```

### 常见错误码

| HTTP状态码 | 说明 |
|-----------|------|
| 400 | 请求参数错误 |
| 503 | Agent未初始化 |
| 500 | 服务器内部错误 |

### 示例

```json
{
  "detail": "Agent not initialized"
}
```

---

## 上下文管理说明

### Token使用监控

系统会自动追踪每个会话的token使用情况：

- **`session_total_tokens`**: 当前会话累积使用的token数（包含压缩摘要+保留消息）
- **`compression_threshold`**: 触发压缩的阈值（默认102,400，即128K的80%）
- **`tokens_until_compression`**: 距离触发压缩还剩多少token

### 自动压缩

当 `session_total_tokens` 超过 `compression_threshold` 时：

1. 系统自动触发压缩算法
2. 保留最近30%的对话内容
3. 将70%的历史内容压缩为XML摘要
4. 节省约60-65%的token
5. **`session_total_tokens` 自动更新**为：压缩摘要tokens + 保留消息tokens

### 智能内容处理（`content` 参数）

当提供 `content` 参数时，系统会**自动判断**使用哪种模式：

#### 计算公式

```
当前可用上下文 = 最大上下文(128K) - (
    会话历史tokens +      # 自动维护（含压缩摘要）
    当前问题tokens +      # 实时计算
    系统提示tokens +      # 预估2000
    预留回答tokens        # 预留4000
)

判断：文档tokens < 当前可用上下文 × 70%
```

#### 两种模式

| 条件 | 模式 | 说明 |
|------|------|------|
| 文档小 | **直接内容模式** | 完整文档放入上下文，更准确 |
| 文档大 | **Recall检索模式** | 向量检索相关片段，节省tokens |

#### 示例

```json
{
  "user_query": "总结这篇论文",
  "content": "论文完整内容...",
  "session_id": "session-123"
}
```

**系统自动处理**：
1. 加载会话历史：5000 tokens
2. 计算当前问题：20 tokens
3. 系统提示估计：2000 tokens
4. 预留回答空间：4000 tokens
5. **可用上下文** = 128000 - 11020 = **116,980 tokens**
6. **判断阈值** = 116,980 × 0.7 = **81,886 tokens**
7. 如果文档 < 81,886 tokens → 直接模式 ✅
8. 如果文档 > 81,886 tokens → Recall模式 🔍

### 建议

- **监控token使用**：通过 `tokens_until_compression` 了解会话状态
- **及时开启新会话**：当token接近阈值时可考虑开启新会话
- **压缩是透明的**：压缩后对话依然连贯，AI可以基于摘要回答问题
- **无需计算tokens**：系统会自动判断最佳处理方式，无需手动指定


# 知识库相关 TODO 任务清单（已更新）

> 基于已有的外部服务接口重新规划任务

## 📋 可用的外部服务

### 1. Mineru 服务 (http://10.0.1.9:7788)
✅ 已部署，可直接调用
- PDF 文档转 Markdown
- 异步任务处理
- 任务状态查询
- 结果获取

### 2. 文档处理服务 (http://localhost:7791 或 http://10.0.169.144:7791)
✅ 已部署，可直接调用
- 文档分块（Chunking）
- 分块向量化（Embedding）
- 存储到 Elasticsearch
- 一体化文档解析（parse-document）
- 列出文档分块
- 关键词搜索
- 编辑块
- 向量召回检索
- 删除文档

---

## 🎯 需要开发的后端任务（按优先级）

### 阶段 1：知识库基础设施（核心，必须）

#### 1.1 数据库模型层
- [ ] 创建 `src/models/knowledge_base.py`
  ```python
  - id: uuid
  - owner_id: uuid (FK -> users.id)
  - name: str
  - description: str
  - tags: List[str]
  - contents_count: int
  - es_index_name: str  # 每个知识库对应的ES索引
  - created_at, updated_at
  ```

- [ ] 创建 `src/models/document.py`
  ```python
  - id: uuid
  - kb_id: uuid (FK -> knowledge_bases.id)
  - name: str
  - size: int
  - status: str (uploading/processing/chunking/embedding/ready/failed)
  - source: str (upload/url)
  - file_path: str (MinIO路径)
  - mineru_task_id: str (Mineru任务ID，可选)
  - parse_task_id: str (文档处理服务任务ID，可选)
  - chunk_count: int (分块数量)
  - error_message: str (错误信息，可选)
  - created_at, updated_at
  ```

#### 1.2 Repository 层
- [ ] 创建 `src/repositories/kb_repository.py`
  - `list_kbs(user_id, query, page, page_size)` - 列出知识库
  - `get_by_id(kb_id, user_id)` - 获取知识库
  - `create(owner_id, name, description, tags)` - 创建知识库
  - `update(kb, **kwargs)` - 更新知识库
  - `delete(kb)` - 删除知识库
  - `calculate_total_size(user_id)` - 计算用户使用的存储空间

- [ ] 创建 `src/repositories/document_repository.py`
  - `list_documents(kb_id, page, page_size)` - 列出文档
  - `get_by_id(doc_id, kb_id)` - 获取文档
  - `create(kb_id, name, size, source, file_path)` - 创建文档记录
  - `update_status(doc_id, status, **kwargs)` - 更新处理状态
  - `delete(doc)` - 删除文档
  - `batch_delete(kb_id, doc_ids)` - 批量删除

#### 1.3 Service 层
- [ ] 创建 `src/services/kb_service.py`
  - `list_kbs()` - 列出知识库
  - `create_kb(user_id, name, description, tags)` - 创建知识库（自动生成ES索引名）
  - `update_kb()` - 更新知识库
  - `delete_kb()` - 删除知识库（级联删除文档、MinIO文件、ES数据）
  - `get_quota(user_id)` - 计算存储使用量

- [ ] 创建 `src/services/document_service.py`
  - `upload_document(kb_id, file)` - 文档上传处理
    1. 上传文件到 MinIO
    2. 创建文档记录（status=uploading）
    3. 调用 Mineru 转换（如果是PDF/Office）
    4. 更新状态为 processing
    5. 调用文档处理服务（分块+向量化+存储ES）
    6. 轮询任务状态，更新文档状态
    7. 完成后更新为 ready
  - `list_documents(kb_id, page, page_size)` - 列出文档
  - `delete_document(kb_id, doc_id)` - 删除文档
    1. 从 ES 删除（调用删除接口）
    2. 从 MinIO 删除文件
    3. 从数据库删除记录
  - `get_document_status(doc_id)` - 获取文档处理状态
  - `list_document_chunks(doc_id, page, page_size)` - 列出文档分块

- [ ] 创建 `src/services/search_service.py`
  - `search_in_kb(kb_id, question, top_n)` - 在知识库中检索
    1. 获取知识库的 ES 索引名
    2. 获取知识库下的所有文档ID列表
    3. 调用召回接口进行检索
    4. 格式化返回结果
  - `keyword_search(kb_id, query, page, page_size)` - 关键词搜索

#### 1.4 工具模块
- [ ] 创建 `src/utils/minio_client.py`
  - `init_minio()` - 初始化 MinIO 客户端
  - `upload_file(bucket, object_name, file_data)` - 上传文件
  - `delete_file(bucket, object_name)` - 删除文件
  - `get_file_url(bucket, object_name)` - 获取预签名 URL
  - `create_bucket_if_not_exists()` - 确保bucket存在

- [ ] 创建 `src/utils/external_services.py`
  - `mineru_convert(file_data, filename)` - 调用 Mineru 转换
  - `mineru_get_task_status(task_id)` - 查询 Mineru 任务状态
  - `mineru_get_content(task_id)` - 获取转换结果
  - `parse_document(file_path, document_id, index_name, ...)` - 调用文档解析服务
  - `get_parse_status(task_id)` - 查询解析任务状态
  - `search_chunks(index_name, doc_ids, question, top_n, ...)` - 调用召回接口
  - `delete_from_es(document_id, index_name)` - 从ES删除文档

#### 1.5 Controller 更新
- [ ] 更新 `src/controllers/kb_controller.py` 中的所有 TODO
  - 实现知识库 CRUD
  - 实现文档上传
  - 实现文档列表
  - 实现文档删除
  - 实现简单检索（调用召回接口，暂不接LLM）

#### 1.6 配置更新
- [ ] 在 `src/config/settings.py` 添加外部服务配置
  ```python
  # External Services
  MINERU_BASE_URL: str = "http://10.0.1.9:7788"
  DOC_PROCESS_BASE_URL: str = "http://localhost:7791"
  ES_HOST: str = "http://10.0.100.36:9201"
  EMBEDDING_MODEL_FACTORY: str = "VLLM"
  EMBEDDING_MODEL_NAME: str = "bge-m3"
  EMBEDDING_BASE_URL: str = "http://localhost:8002/v1"
  ```

---

### 阶段 2：知识广场模块（中等优先级）

#### 2.1 数据库模型
- [ ] 创建 `src/models/hub.py`
- [ ] 创建 `src/models/hub_subscription.py`  
- [ ] 创建 `src/models/hub_post.py`

#### 2.2 Repository 层
- [ ] 创建 `src/repositories/hub_repository.py`
- [ ] 创建 `src/repositories/hub_subscription_repository.py`
- [ ] 创建 `src/repositories/hub_post_repository.py`

#### 2.3 Service 层
- [ ] 创建 `src/services/hub_service.py`
- [ ] 创建 `src/services/hub_post_service.py`

#### 2.4 Controller 更新
- [ ] 实现 `src/controllers/hub_controller.py` 中的 TODO

---

## 📊 任务详细说明

### 核心流程：文档上传与处理

```
用户上传文件
    ↓
1. 上传到 MinIO（我们实现）
    ↓
2. 创建文档记录，status=uploading（我们实现）
    ↓
3. 判断文件类型
    ├─ PDF/Office → 调用 Mineru 转换为 MD
    └─ MD/TXT → 直接使用
    ↓
4. status=processing，调用文档处理服务（7791）
   - 自动完成：分块 + 向量化 + 存储ES
    ↓
5. 轮询任务状态，更新文档记录
    ↓
6. 完成：status=ready，chunk_count=N
```

### 核心流程：知识库检索

```
用户提问
    ↓
1. 获取知识库的 ES index_name（我们实现）
    ↓
2. 获取知识库下所有文档ID列表（我们实现）
    ↓
3. 调用召回接口（7791）进行向量检索
    ↓
4. 格式化返回结果（我们实现）
    - 包含：chunk内容、文档名、相似度分数
    ↓
5. 返回给前端展示
```

---

## 🔧 需要创建的文件清单（精简版）

### 数据模型（2个）
1. `src/models/knowledge_base.py`
2. `src/models/document.py`

### Repository（2个）
3. `src/repositories/kb_repository.py`
4. `src/repositories/document_repository.py`

### Service（3个）
5. `src/services/kb_service.py`
6. `src/services/document_service.py`
7. `src/services/search_service.py`

### 工具类（2个）
8. `src/utils/minio_client.py`
9. `src/utils/external_services.py` - 封装对外部HTTP服务的调用

### Controller（已存在，需完善）
10. `src/controllers/kb_controller.py` - 更新所有TODO

### 配置（已存在，需添加）
11. `src/config/settings.py` - 添加外部服务配置

### 依赖（需添加）
12. `src/requirements.txt` - 添加 httpx（已有）、minio

**总计**：约 **11 个文件**需要创建或修改

---

## ⏱️ 工作量估算（精简后）

| 任务 | 文件数 | 代码行数 | 工作量 |
|---|---:|---:|---|
| 知识库 CRUD | 3 | ~400 | 2天 |
| 文档上传与管理 | 4 | ~600 | 3天 |
| 外部服务集成 | 2 | ~400 | 2天 |
| 检索功能 | 2 | ~300 | 1-2天 |
| **总计** | **11** | **~1700** | **1-2周** |

---

## 📝 实现顺序建议

### Sprint 1：基础功能（3-4天）
1. ✅ 数据库模型（knowledge_bases, documents）
2. ✅ Repository 层
3. ✅ MinIO 客户端封装
4. ✅ 知识库 CRUD Service & Controller

### Sprint 2：文档处理（3-4天）
1. ✅ 外部服务调用封装
   - Mineru 转换接口
   - 文档处理服务接口
2. ✅ 文档上传流程
3. ✅ 状态轮询与更新
4. ✅ 文档列表与删除

### Sprint 3：检索功能（2-3天）
1. ✅ 封装召回接口调用
2. ✅ 知识库检索 API
3. ✅ 结果格式化与返回

---

## 🔄 完整的文档处理流程

### 用户上传文档
```
POST /api/kb/{kb_id}/documents
    ↓
[后端] 1. 上传文件到 MinIO → 获得 file_path
       2. 创建 Document 记录 (status=uploading)
       3. 判断文件类型：
          - PDF/DOCX/PPTX → 调用 Mineru (7788)
          - MD/TXT → 直接读取内容
       4. 更新 status=processing，保存 mineru_task_id
       5. 返回文档ID给前端
    ↓
[后端异步] 6. 轮询 Mineru 任务状态
           7. 完成后获取 Markdown 内容
           8. 调用文档处理服务 (7791) parse-document
              - 自动完成：分块 + 向量化 + 存储ES
           9. 保存 parse_task_id，更新 status=chunking
          10. 轮询解析任务状态
          11. 完成后更新 status=ready，chunk_count=N
          12. 如果失败，更新 status=failed，保存错误信息
```

### 用户检索知识库
```
POST /api/kb/{kb_id}/chat/messages
    ↓
[后端] 1. 获取知识库信息（es_index_name）
       2. 查询知识库下所有文档ID列表
       3. 调用召回接口 (7791) /api/recall
          - 传入: question, index_names, doc_ids
          - 返回: 相关chunks及相似度分数
       4. 格式化结果
          - 提取 content_with_weight
          - 添加文档来源信息
          - 按相似度排序
       5. 返回结果（暂不调用LLM生成答案）
```

---

## 📁 需要创建/修改的文件详细说明

### 1. src/models/knowledge_base.py（新建）
```python
"""Knowledge Base database model."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from config.database import Base
import uuid

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=False, default=list, server_default="{}")
    contents_count = Column(Integer, nullable=False, default=0)
    es_index_name = Column(String, nullable=False, unique=True)  # ES索引名
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 2. src/models/document.py（新建）
```python
"""Document database model."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID
from config.database import Base
import uuid

class Document(Base):
    __tablename__ = "kb_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kb_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False, default=0)
    status = Column(String, nullable=False, default='uploading')  # uploading/processing/chunking/embedding/ready/failed
    source = Column(String, nullable=False)  # upload/url
    file_path = Column(String, nullable=True)  # MinIO路径
    mineru_task_id = Column(String, nullable=True)  # Mineru任务ID
    parse_task_id = Column(String, nullable=True)  # 文档处理任务ID
    chunk_count = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 3. src/utils/minio_client.py（新建）
- 封装 MinIO Python SDK
- 提供文件上传、下载、删除功能

### 4. src/utils/external_services.py（新建）
- 封装对 Mineru (7788) 的 HTTP 调用
- 封装对文档处理服务 (7791) 的 HTTP 调用
- 使用 httpx 进行异步 HTTP 请求

### 5. src/services/kb_service.py（新建）
- 知识库业务逻辑
- ES 索引名生成规则：`kb_{user_id}_{kb_id}`

### 6. src/services/document_service.py（新建）
- 文档处理核心逻辑
- 状态机管理
- 异步任务协调

### 7. src/services/search_service.py（新建）
- 检索逻辑封装
- 结果格式化

---

## ⚠️ 不需要实现的功能

### ❌ 已由外部服务提供（无需开发）
- ~~PDF 解析~~（Mineru提供）
- ~~DOCX 解析~~（Mineru提供）
- ~~文档分块~~（7791提供）
- ~~向量化~~（7791提供）
- ~~向量存储~~（7791提供到ES）
- ~~向量检索~~（7791提供）
- ~~重排序~~（7791提供）

### ❌ 暂不实现
- ~~LLM 问答生成~~（用户明确暂不需要）
- ~~流式响应~~（暂不需要）
- ~~多轮对话~~（暂不需要）

---

## 🎯 关键技术点

### 1. ES 索引命名规则
建议：`kb_{user_id}_{kb_id}`
- 每个知识库一个独立索引
- 便于权限隔离
- 删除知识库时直接删除整个索引

### 2. 文档处理异步流程
使用后台任务（可选方案）：
- **方案A**：定时任务轮询（简单）
- **方案B**：Celery 异步任务（推荐）
- **方案C**：FastAPI BackgroundTasks（轻量）

### 3. 文件类型支持
根据 Mineru 文档，支持：
- ✅ PDF
- ✅ DOCX, XLSX, PPTX
- ✅ Markdown
- ✅ TXT

---

## 📦 需要添加的依赖

```python
# requirements.txt 需要添加
minio==7.2.3           # MinIO客户端（已有）
httpx==0.26.0          # HTTP客户端（已有）
celery==5.3.6          # 异步任务（可选）
```

---

## 🚀 MVP 实现计划（1周）

### Day 1-2：基础模型与 MinIO
- [ ] 数据库模型
- [ ] MinIO 客户端
- [ ] 知识库 CRUD

### Day 3-4：文档上传
- [ ] 文档上传到 MinIO
- [ ] 调用 Mineru 转换
- [ ] 调用文档处理服务
- [ ] 状态轮询

### Day 5-6：检索功能
- [ ] 封装召回接口
- [ ] 实现检索API
- [ ] 结果格式化

### Day 7：测试与优化
- [ ] 端到端测试
- [ ] 错误处理完善
- [ ] 文档编写

---

## 🔗 API 映射关系

### 我们的API → 外部服务

| 我们的接口 | 调用的外部服务 | 说明 |
|---|---|---|
| POST /api/kb/{kb_id}/documents | Mineru: POST /process-async/ | 文档转换 |
| - | 7791: POST /api/parse-document | 分块+向量化+存储 |
| POST /api/kb/{kb_id}/chat/messages | 7791: POST /api/recall | 向量检索 |
| DELETE /api/kb/{kb_id}/documents/{doc_id} | 7791: POST /api/delete-document | 删除ES数据 |
| GET /api/kb/{kb_id}/documents/{doc_id}/chunks | 7791: POST /api/chunk-list | 查看分块 |

---

## 📌 注意事项

1. **ES 索引管理**
   - 每个用户的所有知识库可以共用一个索引
   - 通过 document_id 区分不同文档
   - 索引名建议：`user_{user_id}_kb`

2. **异步任务处理**
   - Mineru 和文档处理都是异步的
   - 需要实现轮询或webhook机制
   - 建议使用 FastAPI BackgroundTasks 先做简单实现

3. **错误处理**
   - 外部服务调用失败需要妥善处理
   - 更新文档状态为 failed
   - 记录错误信息

4. **文件清理**
   - 删除文档时需要：
     - 删除 MinIO 文件
     - 删除 ES 中的 chunks
     - 删除数据库记录

---

这是基于你提供的外部服务重新规划的 TODO 清单，工作量从原来的 5-8 周缩减到 **1-2 周**！

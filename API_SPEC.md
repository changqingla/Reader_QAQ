# Reader_QAQ 后端接口设计（草案）

> 目标：支撑当前前端项目的全部交互功能；所有接口均为示例草案，可按实际后端架构调整路径、鉴权与字段。默认使用 JSON，除文件上传为 multipart/form-data。

## 统一规范
- 认证：HTTP Header `Authorization: Bearer <token>`（除登录/公开列表外）。
- 分页：`page`（默认1），`pageSize`（默认20）。返回 `total`, `page`, `pageSize`, `items`。
- 时间：统一 ISO8601 UTC（示例 `2025-01-10T12:30:00Z`）。
- 成功返回建议统一：
```json
{ "data": { /* 资源主体 */ }, "meta": { /* 分页/游标等 */ } }
```

- 错误返回
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "参数不合法",
    "details": {"field": "reason"}
  }
}
```

常见错误码表：

| code | http | 说明 |
|---|---|---|
| UNAUTHORIZED | 401 | 未登录/凭证失效 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突（如已存在/状态不允许） |
| PAYLOAD_TOO_LARGE | 413 | 上传过大 |
| RATE_LIMITED | 429 | 触发限流，建议重试间隔 |
| INTERNAL_ERROR | 500 | 服务内部错误 |

### 状态码与错误示例清单表

| 场景 | HTTP | code | 示例 |
|---|---:|---|---|
| 未登录/令牌过期 | 401 | UNAUTHORIZED | `{ "error": { "code": "UNAUTHORIZED", "message": "token expired" } }` |
| 权限不足 | 403 | FORBIDDEN | `{ "error": { "code": "FORBIDDEN", "message": "not allowed" } }` |
| 资源不存在 | 404 | NOT_FOUND | `{ "error": { "code": "NOT_FOUND", "message": "kb not found", "details": {"kbId":"kb_x"} } }` |
| 资源冲突 | 409 | CONFLICT | `{ "error": { "code": "CONFLICT", "message": "name already exists" } }` |
| 上传超限 | 413 | PAYLOAD_TOO_LARGE | `{ "error": { "code": "PAYLOAD_TOO_LARGE", "message": "file too large (max 100MB)" } }` |
| 速率限制 | 429 | RATE_LIMITED | `{ "error": { "code": "RATE_LIMITED", "message": "too many requests" }, "meta": { "retryAfter": 30 } }` |
| 校验失败 | 400 | VALIDATION_ERROR | `{ "error": { "code": "VALIDATION_ERROR", "message": "invalid body", "details": {"field":"name"} } }` |
| 服务器错误 | 500 | INTERNAL_ERROR | `{ "error": { "code": "INTERNAL_ERROR", "message": "unexpected" } }` |

---

## 1. 鉴权 Auth（可选）
### 1.1 登录
POST `/api/auth/login`
```json
{ "email": "user@example.com", "password": "***" }
```
```json
{ "token": "<jwt>", "user": {"id": "u_1", "name": "Alice", "avatar": null} }
```

### 1.2 当前用户
GET `/api/auth/me`
```json
{ "id": "u_1", "name": "Alice", "avatar": null }
```

---

## 2. 我的知识库 Knowledge Bases
> 覆盖 `/knowledge/default` 与侧边栏 “我的知识库”。

### 2.1 列出我的知识库
GET `/api/kb`
- Query: `q?`（搜索），`page?`, `pageSize?`
```json
{ "total": 2, "page": 1, "pageSize": 20, "items": [
  {"id": "kb_default", "name": "默认知识库", "description": "系统自动创建", "tags": [], "contents": 0, "createdAt": "2025-01-01"},
  {"id": "kb_2", "name": "AI 技术前沿", "description": "", "tags": ["AI","研究"], "contents": 12, "createdAt": "2025-01-10"}
]}
```

### 2.2 创建知识库
POST `/api/kb`
```json
{ "name": "产品设计精选", "description": "精选案例", "tags": ["设计","UX"] }
```
```json
{ "id": "kb_3" }
```

### 2.3 更新知识库
PATCH `/api/kb/{kbId}`
```json
{ "name?": "新名称", "description?": "概述", "tags?": ["tag1","tag2"] }
```
```json
{ "success": true }
```

### 2.4 删除知识库
DELETE `/api/kb/{kbId}` → `{ "success": true }`

### 2.5 存储配额/用量
GET `/api/kb/quota`
```json
{ "usedBytes": 1234567, "limitBytes": 500000000000 }
```

---

## 3. 知识库文档管理 Documents
> 上传文件/添加网页、列表与删除。

### 3.1 上传文档
POST `/api/kb/{kbId}/documents` (multipart/form-data)
- form fields:
  - `file`: 文件
  - `metadata?`: 可选 JSON 字符串（如 `{"source":"upload"}`）
```json
{ "id": "doc_1", "name": "paper.pdf", "size": 102400, "status": "processing" }
```

### 3.2 通过 URL 添加网页
POST `/api/kb/{kbId}/documents:fromUrl`
```json
{ "url": "https://example.com/article", "sync": false, "depth": 0, "capture": "markdown" }
```
```json
{ "id": "doc_2", "name": "article", "status": "processing" }
```

### 3.3 列出文档
GET `/api/kb/{kbId}/documents` + 分页
```json
{ "total": 2, "page": 1, "pageSize": 20, "items": [
  {"id":"doc_1","name":"paper.pdf","size":102400,"createdAt":"2025-01-10"},
  {"id":"doc_2","name":"article","size":0,"createdAt":"2025-01-11"}
]}
```

### 3.4 删除文档
DELETE `/api/kb/{kbId}/documents/{docId}` → `{ "success": true }`

### 3.5 批量删除文档
POST `/api/kb/{kbId}/documents:batchDelete`
```json
{ "ids": ["doc_1","doc_2"] }
```
```json
{ "success": true }
```

### 3.6 文档处理状态
GET `/api/kb/{kbId}/documents/{docId}/status`
```json
{ "data": { "status": "processing|ready|failed", "errorMessage": null } }
```

---

## 4. 知识库问答 Chat（对 KB 提问）
> 覆盖 `/knowledge/default` 与 `/knowledge/hub/:id` 右侧提问区。

### 4.1 发送提问
POST `/api/kb/{kbId}/chat/messages`
```json
{ "question": "请总结这个知识库的关键观点", "contextDocs?": ["doc_1"], "mode?": "insight|timeline|summary" }
```
```json
{ "messageId": "m_1", "answer": "……", "references": [{"docId":"doc_1","snippet":"…"}] }
```

### 4.2 历史记录（可选）
GET `/api/kb/{kbId}/chat/messages?page=1&pageSize=20`
```json
{ "total": 3, "items": [{"id":"m_1","question":"…","answer":"…","createdAt":"…"}] }
```

---

## 5. 知识广场 Knowledge Hub（公开）
> 覆盖 `/knowledge` 与 `/knowledge/hub/:hubId` 列表、详情、帖子内容与订阅。

### 5.1 列表/搜索广场
GET `/api/hub` + `q?`, `page`, `pageSize`
```json
{ "total": 100, "items": [{"id":"1","title":"DeepSeek 知识库","desc":"…","icon":"📘","subs":210,"contents":40}] }
```

### 5.2 获取广场详情
GET `/api/hub/{hubId}`
```json
{ "id":"1","title":"笔记本科普与选购","icon":"💻","subs":86,"contents":311, "isSubscribed": false }
```

### 5.3 列出帖子
GET `/api/hub/{hubId}/posts?page=1&pageSize=20`
```json
{ "total": 311, "items": [{"id":"p_1","title":"…","author":"鹿鹿","date":"10-20","preview":"…"}] }
```

> 所有列表类接口统一支持：`order?=asc|desc`，`sortBy?=createdAt|updatedAt|title`；也可选择游标分页：`cursor?` 与 `limit?`，返回 `{ meta: { nextCursor } }`。

### 5.4 获取帖子内容
GET `/api/hub/{hubId}/posts/{postId}`
```json
{ "id":"p_1","title":"…","author":"鹿鹿","date":"2025-10-20","tags":["笔记本"], "content":"markdown 或 html 内容" }
```

### 5.5 订阅 / 取消订阅
POST `/api/hub/{hubId}/subscribe` → `{ "success": true }`
DELETE `/api/hub/{hubId}/subscribe` → `{ "success": true }`

---

## 6. 收藏 Favorites
> 覆盖 `/favorites`（收藏单篇论文/帖子或整个知识库）。

### 6.1 列出收藏
GET `/api/favorites` + `type?=paper|knowledge`, `q?`, `page`, `pageSize`
```json
{ "total": 6, "items": [
  {"id":"fav_1","type":"paper","title":"Attention Is All You Need","description":"…","author":"Vaswani","date":"2023-12-15","source":"arXiv","tags":["NLP","Transformer"]},
  {"id":"fav_2","type":"knowledge","title":"AI 技术前沿","description":"…","date":"2024-01-10","tags":["AI","研究"]}
]}
```

### 6.2 添加收藏
POST `/api/favorites`
```json
{ "type": "paper|knowledge", "targetId": "p_1 或 kb_1", "tags?": ["tag"] }
```
```json
{ "id": "fav_123" }
```

### 6.2.1 一键切换收藏（可选）
POST `/api/favorites:toggle`
```json
{ "type": "paper|knowledge", "targetId": "p_1 或 kb_1" }
```
```json
{ "data": { "id": "fav_123", "active": true } }
```

### 6.3 移除收藏
DELETE `/api/favorites/{favoriteId}` → `{ "success": true }`

### 6.4 更新收藏标签（可选）
PATCH `/api/favorites/{favoriteId}`
```json
{ "tags": ["学习","精读"] }
```

---

## 7. 备忘录 Notes
> 覆盖 `/notes` 三栏结构（文件夹/列表/编辑）。

### 7.1 列出文件夹
GET `/api/notes/folders`
```json
{ "items": [{"id":"f_all","name":"全部","count":42},{"id":"f_work","name":"工作","count":18}] }
```

### 7.2 新建/重命名/删除文件夹
POST `/api/notes/folders` → `{ "id": "f_new" }`
PATCH `/api/notes/folders/{folderId}` `{ "name": "新名称" }`
DELETE `/api/notes/folders/{folderId}` → `{ "success": true }`

### 7.3 列出笔记
GET `/api/notes?folderId=f_work&q=&page=1&pageSize=20`
```json
{ "total": 20, "items": [{"id":"n_1","title":"会议记录","updatedAt":"2025-01-20","tags":["会议"],"folder":"工作"}] }
```

### 7.4 获取笔记详情
GET `/api/notes/{noteId}`
```json
{ "id":"n_1","title":"会议记录","content":"文本/Markdown","folder":"工作","tags":["会议","项目"],"updatedAt":"2025-01-20" }
```

### 7.5 新建/更新/删除笔记
POST `/api/notes`
```json
{ "title": "新笔记", "content": "…", "folder": "工作", "tags": ["标签"] }
```
PATCH `/api/notes/{noteId}`
```json
{ "title?": "更新标题", "content?": "更新内容", "folder?": "工作", "tags?": ["标签"] }
```
DELETE `/api/notes/{noteId}` → `{ "success": true }`

### 7.6 批量删除笔记（可选）
POST `/api/notes:batchDelete`
```json
{ "ids": ["n_1","n_2"] }
```
```json
{ "success": true }
```

### 7.7 AI 润色（可选）
POST `/api/notes/{noteId}:polish`
```json
{ "rules": ["normalize-bullets","trim-trailing","squash-blank"] }
```
```json
{ "content": "润色后的文本内容" }
```

---

---

## 8. 上传与静态内容（通用）
### 8.1 直传签名（可选）
POST `/api/uploads/sign`
```json
{ "filename": "paper.pdf", "contentType": "application/pdf" }
```

### 8.2 健康检查（可选）
GET `/api/health`
```json
{ "status": "ok", "version": "1.0.0" }
```

### 8.3 刷新令牌（可选）
POST `/api/auth/refresh`
```json
{ "refreshToken": "<token>" }
```
```json
{ "token": "<jwt>" }
```
# Reader_QAQ PostgreSQL 数据库设计（草案）

> 以支持 API_SPEC.md 中定义的能力为目标。命名采用 snake_case。时间戳使用 timestamptz（UTC）。主键建议 uuid。

## 全局约定
- id 使用 `uuid`（或 `text` 存储外部生成 id），示例采用 `uuid`。
- 默认字段：`created_at timestamptz NOT NULL DEFAULT now()`，`updated_at timestamptz NOT NULL DEFAULT now()`。
- 可选软删除：`deleted_at timestamptz`（如需要）。

---

## 1. 用户与鉴权
### users
- id uuid PK
- email text UNIQUE NOT NULL
- password_hash text NOT NULL
- name text NOT NULL
- avatar text NULL
- created_at, updated_at

```sql
CREATE TABLE users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  name text NOT NULL,
  avatar text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
```

### refresh_tokens（可选）
- id uuid PK
- user_id uuid FK -> users.id
- token text UNIQUE NOT NULL
- expires_at timestamptz NOT NULL
- created_at

---

## 2. 知识库
### knowledge_bases
- id uuid PK
- owner_id uuid FK -> users.id
- name text NOT NULL
- description text NULL
- tags text[] NOT NULL DEFAULT '{}'
- contents_count int NOT NULL DEFAULT 0
- created_at, updated_at

```sql
CREATE TABLE knowledge_bases (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name text NOT NULL,
  description text,
  tags text[] NOT NULL DEFAULT '{}',
  contents_count int NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_kb_owner ON knowledge_bases(owner_id);
CREATE INDEX idx_kb_name_trgm ON knowledge_bases USING gin (name gin_trgm_ops);
```

### kb_documents（知识库文档）
- id uuid PK
- kb_id uuid FK -> knowledge_bases.id
- name text NOT NULL
- size bigint NOT NULL DEFAULT 0
- status text NOT NULL CHECK (status IN ('processing','ready','failed'))
- source text NULL -- upload, url
- url text NULL -- 当来源为 URL
- created_at, updated_at

```sql
CREATE TABLE kb_documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  kb_id uuid NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
  name text NOT NULL,
  size bigint NOT NULL DEFAULT 0,
  status text NOT NULL CHECK (status IN ('processing','ready','failed')),
  source text,
  url text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_kb_docs_kb ON kb_documents(kb_id);
```

### kb_chat_messages（问答记录，可选）
- id uuid PK
- kb_id uuid FK -> knowledge_bases.id
- user_id uuid FK -> users.id
- question text NOT NULL
- answer text NULL
- mode text NULL -- insight/timeline/summary
- created_at timestamptz NOT NULL DEFAULT now()

---

## 3. 知识广场（公开 Hub）
### hubs
- id uuid PK
- title text NOT NULL
- description text NULL
- icon text NULL
- subscribers_count int NOT NULL DEFAULT 0
- contents_count int NOT NULL DEFAULT 0
- created_at, updated_at

```sql
CREATE TABLE hubs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  description text,
  icon text,
  subscribers_count int NOT NULL DEFAULT 0,
  contents_count int NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_hubs_title_trgm ON hubs USING gin (title gin_trgm_ops);
```

### hub_subscriptions（订阅关系）
- id uuid PK
- hub_id uuid FK -> hubs.id
- user_id uuid FK -> users.id
- created_at timestamptz NOT NULL DEFAULT now()
- UNIQUE(hub_id, user_id)

### hub_posts（帖子/文章）
- id uuid PK
- hub_id uuid FK -> hubs.id
- author_id uuid FK -> users.id NULL -- 对外抓取的可为空
- title text NOT NULL
- preview text NULL
- content text NULL -- markdown/html
- published_at timestamptz NULL
- created_at, updated_at

```sql
CREATE TABLE hub_posts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  hub_id uuid NOT NULL REFERENCES hubs(id) ON DELETE CASCADE,
  author_id uuid REFERENCES users(id) ON DELETE SET NULL,
  title text NOT NULL,
  preview text,
  content text,
  published_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_posts_hub ON hub_posts(hub_id);
CREATE INDEX idx_posts_published ON hub_posts(published_at);
```

---

## 4. 收藏
### favorites
- id uuid PK
- user_id uuid FK -> users.id
- type text NOT NULL CHECK (type IN ('paper','knowledge'))
- target_id text NOT NULL -- 对应 hub_posts.id 或 knowledge_bases.id
- tags text[] NOT NULL DEFAULT '{}'
- created_at timestamptz NOT NULL DEFAULT now()
- UNIQUE(user_id, type, target_id)

---

## 5. 笔记 Notes
### note_folders
- id uuid PK
- user_id uuid FK -> users.id
- name text NOT NULL
- created_at, updated_at
- UNIQUE(user_id, name)

### notes
- id uuid PK
- user_id uuid FK -> users.id
- folder_id uuid FK -> note_folders.id
- title text NOT NULL
- content text NOT NULL
- tags text[] NOT NULL DEFAULT '{}'
- updated_at timestamptz NOT NULL DEFAULT now()
- created_at timestamptz NOT NULL DEFAULT now()

```sql
CREATE TABLE note_folders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(user_id, name)
);

CREATE TABLE notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  folder_id uuid NOT NULL REFERENCES note_folders(id) ON DELETE SET NULL,
  title text NOT NULL,
  content text NOT NULL,
  tags text[] NOT NULL DEFAULT '{}',
  updated_at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_notes_user ON notes(user_id);
CREATE INDEX idx_notes_folder ON notes(folder_id);
CREATE INDEX idx_notes_title_trgm ON notes USING gin (title gin_trgm_ops);
```

---

## 6. 审计（可选）
### audits
- id uuid PK
- user_id uuid FK -> users.id
- action text NOT NULL -- kb.upload / kb.delete / kb.chat / notes.create 等
- resource_type text NULL
- resource_id text NULL
- payload jsonb NULL
- created_at timestamptz NOT NULL DEFAULT now()

```sql
CREATE TABLE audits (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE SET NULL,
  action text NOT NULL,
  resource_type text,
  resource_id text,
  payload jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_audits_action ON audits(action);
CREATE INDEX idx_audits_created ON audits(created_at);
```

---

## 7. 触发器（可选）
- `updated_at` 自动更新触发器。
- `knowledge_bases.contents_count` 可通过文档插入/删除触发器维护。

```sql
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为需要的表添加触发器
CREATE TRIGGER t_kb_updated BEFORE UPDATE ON knowledge_bases
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER t_doc_updated BEFORE UPDATE ON kb_documents
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER t_hub_updated BEFORE UPDATE ON hubs
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER t_post_updated BEFORE UPDATE ON hub_posts
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER t_note_updated BEFORE UPDATE ON notes
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

> 注：需要相似度搜索/全文检索时，可在 `kb_documents`、`hub_posts`、`notes` 上增加 `tsvector` 列与 GIN 索引；或引入向量库（pgvector）分别维护嵌入向量表。


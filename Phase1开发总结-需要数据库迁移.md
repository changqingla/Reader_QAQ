# Phase 1 开发总结 - 重要提示

## ⚠️ 重要：需要数据库迁移

当前已完成后端核心模块的代码修改，但**必须先进行数据库迁移才能继续**。

### 已完成的代码改动

1. ✅ **数据库模型** (`src/models/knowledge_base.py`)
   - 移除 `tags` 字段
   - 添加 `category`, `is_public`, `subscribers_count`, `view_count`, `last_updated_at` 字段
   - 创建 `KnowledgeBaseSubscription` 模型

2. ✅ **Repository 层**
   - `KBSubscriptionRepository` - 完整的订阅功能
   - `KnowledgeBaseRepository` - 支持公开知识库、分类查询、年度精选

3. 🔄 **下一步**
   - Service 层更新
   - Controller 层更新
   - 前端更新

## 📊 需要的数据库迁移 SQL

```sql
-- 1. 修改 knowledge_bases 表
ALTER TABLE knowledge_bases 
  -- 移除 tags 列（如果需要保留旧数据，先备份）
  DROP COLUMN IF EXISTS tags,
  
  -- 添加新列
  ADD COLUMN IF NOT EXISTS category VARCHAR(50) NOT NULL DEFAULT '其它',
  ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS subscribers_count INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS view_count INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMP;

-- 2. 创建索引
CREATE INDEX IF NOT EXISTS idx_kb_category ON knowledge_bases(category);
CREATE INDEX IF NOT EXISTS idx_kb_public ON knowledge_bases(is_public);
CREATE INDEX IF NOT EXISTS idx_kb_subscribers ON knowledge_bases(subscribers_count DESC);

-- 3. 创建订阅表
CREATE TABLE IF NOT EXISTS kb_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kb_id UUID NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    subscribed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_viewed_at TIMESTAMP,
    UNIQUE(user_id, kb_id)
);

CREATE INDEX IF NOT EXISTS idx_subscription_user ON kb_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_kb ON kb_subscriptions(kb_id);

-- 4. 数据迁移（可选）
-- 如果有现有数据，可以根据描述或名称智能分类
-- 示例：根据关键词分配分类
UPDATE knowledge_bases SET category = '工学' 
WHERE name ILIKE '%AI%' OR name ILIKE '%机器学习%' OR name ILIKE '%编程%';

UPDATE knowledge_bases SET category = '经济学'
WHERE name ILIKE '%经济%' OR name ILIKE '%金融%' OR name ILIKE '%商业%';

-- 其他根据实际情况添加...
```

## 🚀 执行迁移的方式

### 方式 1：使用 Docker 重启（推荐）

如果使用 Docker 并且可以接受数据清空：

```bash
cd /data/ht/workspace/Reader_QAQ/docker
docker-compose down -v
docker-compose up -d
```

### 方式 2：手动执行 SQL

连接到 PostgreSQL 数据库并执行上面的 SQL：

```bash
# 进入数据库容器
docker exec -it <postgres_container_name> psql -U <username> -d <database>

# 或者使用 pgAdmin / DBeaver 等工具
```

### 方式 3：使用迁移脚本（最安全）

创建迁移脚本保留现有数据：

```python
# migrations/add_kb_sharing.py
async def upgrade(conn):
    # 备份
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_bases_backup AS 
        SELECT * FROM knowledge_bases;
    """)
    
    # 执行迁移
    # ... (执行上面的 SQL)
```

## ⏭️ 迁移后继续的开发步骤

1. 重启后端服务
2. 完成 Service 层更新
3. 完成 Controller 层更新  
4. 更新前端 API schemas
5. 重构前端组件

## 💾 备份建议

**在执行迁移前，强烈建议：**
1. 备份当前数据库
2. 备份重要知识库数据
3. 在测试环境先验证

## 🔄 如何验证迁移成功

迁移后，执行以下查询验证：

```sql
-- 检查新列是否存在
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'knowledge_bases';

-- 检查订阅表是否创建
SELECT * FROM kb_subscriptions LIMIT 1;

-- 检查索引是否创建
SELECT indexname FROM pg_indexes 
WHERE tablename = 'knowledge_bases' OR tablename = 'kb_subscriptions';
```

## ❓ 问题处理

如果遇到问题：
1. 检查数据库日志
2. 检查列冲突
3. 检查约束冲突
4. 联系管理员

---

**准备好进行数据库迁移了吗？** 
请告诉我使用哪种方式，然后我们继续完成剩余的开发工作。


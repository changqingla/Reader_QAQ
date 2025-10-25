-- ============================================
-- Reader QAQ - 知识库共享功能数据库迁移脚本
-- ============================================
-- 
-- 执行方式:
--   方式1: docker exec -i <postgres_container> psql -U <username> -d <database> < 数据库迁移脚本.sql
--   方式2: 使用 pgAdmin 或 DBeaver 等工具连接数据库并执行
--   方式3: Docker 重启（会清空所有数据）: docker-compose down -v && docker-compose up -d
--
-- 注意: 执行前请备份数据库！
-- ============================================

-- 开始事务
BEGIN;

-- 1. 修改 knowledge_bases 表
-- ============================================

-- 1.1 删除 tags 列（如果存在）
-- 注意：如果需要保留旧数据，请先备份 tags 列的数据
ALTER TABLE knowledge_bases DROP COLUMN IF EXISTS tags;

-- 1.2 添加新列
ALTER TABLE knowledge_bases 
  ADD COLUMN IF NOT EXISTS category VARCHAR(50) NOT NULL DEFAULT '其它',
  ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS subscribers_count INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS view_count INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMP;

-- 1.3 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_kb_category ON knowledge_bases(category);
CREATE INDEX IF NOT EXISTS idx_kb_public ON knowledge_bases(is_public);
CREATE INDEX IF NOT EXISTS idx_kb_subscribers ON knowledge_bases(subscribers_count DESC);

-- 1.4 数据迁移（可选）：根据知识库名称/描述智能分配分类
-- 如果有现有数据，可以根据关键词自动分类
UPDATE knowledge_bases SET category = '工学' 
WHERE (name ILIKE '%AI%' OR name ILIKE '%机器学习%' OR name ILIKE '%编程%' OR name ILIKE '%技术%' OR name ILIKE '%DeepSeek%')
  AND category = '其它';

UPDATE knowledge_bases SET category = '经济学'
WHERE (name ILIKE '%经济%' OR name ILIKE '%金融%' OR name ILIKE '%商业%' OR name ILIKE '%投资%')
  AND category = '其它';

UPDATE knowledge_bases SET category = '管理学'
WHERE (name ILIKE '%管理%' OR name ILIKE '%团队%' OR name ILIKE '%项目%')
  AND category = '其它';

UPDATE knowledge_bases SET category = '文学'
WHERE (name ILIKE '%文学%' OR name ILIKE '%小说%' OR name ILIKE '%诗歌%')
  AND category = '其它';

UPDATE knowledge_bases SET category = '历史学'
WHERE (name ILIKE '%历史%' OR name ILIKE '%考古%')
  AND category = '其它';

-- 更多分类规则可以根据实际情况添加...

-- 2. 创建订阅表
-- ============================================

CREATE TABLE IF NOT EXISTS kb_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kb_id UUID NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    subscribed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_viewed_at TIMESTAMP,
    CONSTRAINT uq_user_kb_subscription UNIQUE(user_id, kb_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_subscription_user ON kb_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_kb ON kb_subscriptions(kb_id);
CREATE INDEX IF NOT EXISTS idx_subscription_time ON kb_subscriptions(subscribed_at DESC);

-- 3. 验证迁移
-- ============================================

-- 检查新列是否存在
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='knowledge_bases' AND column_name='category') THEN
        RAISE EXCEPTION '迁移失败: category 列不存在';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='knowledge_bases' AND column_name='is_public') THEN
        RAISE EXCEPTION '迁移失败: is_public 列不存在';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='kb_subscriptions') THEN
        RAISE EXCEPTION '迁移失败: kb_subscriptions 表不存在';
    END IF;
    
    RAISE NOTICE '✓ 迁移验证通过';
END $$;

-- 显示迁移后的表结构
\d knowledge_bases
\d kb_subscriptions

-- 提交事务
COMMIT;

-- ============================================
-- 迁移完成！
-- ============================================
-- 
-- 验证步骤:
-- 1. 检查 knowledge_bases 表的列: SELECT * FROM information_schema.columns WHERE table_name = 'knowledge_bases';
-- 2. 检查 kb_subscriptions 表: SELECT * FROM kb_subscriptions LIMIT 1;
-- 3. 检查索引: SELECT indexname FROM pg_indexes WHERE tablename IN ('knowledge_bases', 'kb_subscriptions');
-- 4. 重启后端服务: docker restart <backend_container> 或手动重启
-- 
-- 如果遇到问题:
-- - 回滚: ROLLBACK; (如果还在事务中)
-- - 恢复备份: pg_restore ...
-- 
-- ============================================

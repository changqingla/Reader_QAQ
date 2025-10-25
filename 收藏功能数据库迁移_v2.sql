-- ===================================================================
-- 收藏功能数据库迁移脚本 v2
-- 适用于 PostgreSQL
-- 创建时间: 2025-10-25
-- 功能: 删除旧的 favorites 表，创建新的统一收藏表
-- ===================================================================

BEGIN;

-- 1. 备份现有 favorites 表数据（如果需要）
-- 取消下面注释来创建备份表
/*
CREATE TABLE favorites_backup AS SELECT * FROM favorites;
RAISE NOTICE '✓ 旧数据已备份到 favorites_backup 表';
*/

-- 2. 删除旧的 favorites 表
DROP TABLE IF EXISTS favorites CASCADE;

-- 3. 创建新的 favorites 表
CREATE TABLE favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    item_type VARCHAR(20) NOT NULL,  -- 'knowledge_base' 或 'document'
    item_id UUID NOT NULL,
    source VARCHAR(20),               -- 'subscription' 或 'manual'
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 外键约束
    CONSTRAINT fk_favorites_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    
    -- 唯一约束：一个用户对同一项目只能收藏一次
    CONSTRAINT uq_user_item_favorite
        UNIQUE (user_id, item_type, item_id)
);

-- 4. 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user_type ON favorites(user_id, item_type);
CREATE INDEX IF NOT EXISTS idx_favorites_created ON favorites(created_at DESC);

-- 5. 添加注释
COMMENT ON TABLE favorites IS '收藏表：统一管理知识库和文档收藏';
COMMENT ON COLUMN favorites.user_id IS '用户ID';
COMMENT ON COLUMN favorites.item_type IS '收藏类型：knowledge_base 或 document';
COMMENT ON COLUMN favorites.item_id IS '收藏项目ID（知识库ID或文档ID）';
COMMENT ON COLUMN favorites.source IS '收藏来源：subscription（订阅自动收藏）或 manual（手动收藏）';
COMMENT ON COLUMN favorites.created_at IS '收藏时间';

-- 6. 验证迁移是否成功
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_name = 'favorites'
    ) THEN
        RAISE NOTICE '✓ 新的 favorites 表创建成功';
    ELSE
        RAISE EXCEPTION '✗ favorites 表创建失败';
    END IF;
    
    -- 验证字段是否正确
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'favorites' 
        AND column_name = 'item_type'
    ) THEN
        RAISE NOTICE '✓ 表结构验证通过';
    ELSE
        RAISE EXCEPTION '✗ 表结构验证失败';
    END IF;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '✓ 收藏功能数据库迁移完成！';
    RAISE NOTICE '========================================';
END $$;

COMMIT;

-- ===================================================================
-- 数据迁移示例（如果需要从旧表迁移数据）
-- ===================================================================
/*
BEGIN;

-- 将旧的 'knowledge' 类型收藏迁移到新表
INSERT INTO favorites (user_id, item_type, item_id, source, created_at)
SELECT 
    user_id,
    'knowledge_base' as item_type,
    target_id::uuid as item_id,
    'manual' as source,
    created_at
FROM favorites_backup
WHERE type = 'knowledge'
ON CONFLICT (user_id, item_type, item_id) DO NOTHING;

RAISE NOTICE '✓ 知识库收藏数据迁移完成';

-- 注意：旧表中的 'paper' 类型需要根据业务逻辑决定如何处理
-- 如果 'paper' 对应新的 'document'，可以类似迁移

COMMIT;
*/


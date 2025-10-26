/**
 * 知识广场页面
 * 显示公开知识库、支持分类浏览、2025精选列表
 */
import React, { useState, useEffect, useMemo } from 'react';
import { Search, Plus, Database, Users, ChevronDown, ChevronUp } from 'lucide-react';
import Sidebar from '@/components/Sidebar/Sidebar';
import KnowledgeSidebar from '@/components/KnowledgeSidebar/KnowledgeSidebar';
import CreateKnowledgeModal from '@/components/CreateKnowledgeModal/CreateKnowledgeModal';
import EditKnowledgeModal from '@/components/EditKnowledgeModal/EditKnowledgeModal';
import { api, kbAPI } from '@/lib/api';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/useToast';
import { useChatSessions } from '@/hooks/useChatSessions';
import { KNOWLEDGE_CATEGORIES, CATEGORY_ICONS } from '@/constants/categories';
import styles from './Knowledge.module.css';

// 默认展示的 5 个分类
const DEFAULT_CATEGORIES = ['工学', '经济学', '管理学', '文学', '历史学'];

export default function Knowledge() {
  const navigate = useNavigate();
  const toast = useToast();
  const { chatSessions, refreshSessions } = useChatSessions();
  
  // UI State
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState(false);
  
  // Modal State
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [kbToEdit, setKbToEdit] = useState<any>(null);
  
  // Data State
  const [myKnowledgeBases, setMyKnowledgeBases] = useState<any[]>([]);
  const [publicKbs, setPublicKbs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Filter State
  const [query, setQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('2025精选');

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  useEffect(() => {
    loadPublicKBs();
  }, [activeCategory, query]);

  const loadKnowledgeBases = async () => {
    try {
      const response = await kbAPI.listKnowledgeBases();
      setMyKnowledgeBases(response.items);
    } catch (error: any) {
      console.error('Failed to load knowledge bases:', error);
    }
  };

  const loadPublicKBs = async () => {
    setLoading(true);
    try {
      if (activeCategory === '2025精选') {
        const { items } = await kbAPI.listFeatured(1, 30);
        setPublicKbs(items);
      } else {
        const { items } = await kbAPI.listPublicKBs(
          activeCategory,
          query || undefined,
          1,
          20
        );
        setPublicKbs(items);
      }
    } catch (error) {
      console.error('加载公开知识库失败:', error);
      setPublicKbs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKB = async (data: { name: string; description: string; category: string }) => {
    try {
      await kbAPI.createKnowledgeBase(data.name, data.description, data.category);
      await loadKnowledgeBases();
      toast.success('知识库创建成功！');
    } catch (error: any) {
      toast.error(error.message || '创建知识库失败');
    }
  };

  const handleEditKB = (kb: any) => {
    setKbToEdit(kb);
    setIsEditModalOpen(true);
  };

  const handleSaveKB = async (data: { name: string; description: string; category: string }) => {
    if (!kbToEdit) return;
    try {
      await kbAPI.updateKnowledgeBase(kbToEdit.id, data);
      await loadKnowledgeBases();
      toast.success('知识库已更新');
      setIsEditModalOpen(false);
      setKbToEdit(null);
    } catch (error: any) {
      toast.error(error.message || '更新失败');
    }
  };

  const handleDeleteKB = async (kbId: string) => {
    try {
      await kbAPI.deleteKnowledgeBase(kbId);
      await loadKnowledgeBases();
      toast.success('知识库已删除');
    } catch (error: any) {
      toast.error(error.message || '删除失败');
    }
  };

  const handleCategoryClick = (category: string) => {
    setActiveCategory(category);
    setExpandedCategories(false);
  };

  const handleKBClick = (kbId: string) => {
    navigate(`/knowledge/${kbId}`);
  };

  // 获取可折叠的分类
  const hiddenCategories = useMemo(() => {
    return KNOWLEDGE_CATEGORIES.filter(cat => !DEFAULT_CATEGORIES.includes(cat));
  }, []);

  // 聊天处理函数
  const handleNewChat = () => {
    navigate('/');
  };

  const handleSelectChat = (chatId: string) => {
    navigate('/');
  };

  const handleDeleteChat = async (chatId: string) => {
    try {
      await api.deleteChatSession(chatId);
      await refreshSessions();
      toast.success('对话已删除');
    } catch (error) {
      console.error('Failed to delete chat:', error);
      toast.error('删除对话失败');
    }
  };

  return (
    <div className={styles.page}>
      {isMobile && isSidebarOpen && (
        <div className={styles.overlay} onClick={() => setIsSidebarOpen(false)} />
      )}

      <div className={`${styles.sidebarContainer} ${isMobile && isSidebarOpen ? styles.open : ''}`}>
        <Sidebar 
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
          chats={chatSessions}
        />
      </div>

      {/* Modals */}
      <CreateKnowledgeModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateKB}
      />

      {kbToEdit && (
        <EditKnowledgeModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setKbToEdit(null);
          }}
          onSave={handleSaveKB}
          initialData={{
            name: kbToEdit.name,
            description: kbToEdit.description,
            category: kbToEdit.category || '其它'
          }}
        />
      )}

      <div className={styles.main}>
        <div className={styles.contentArea}>
          {/* Knowledge Sidebar */}
          <KnowledgeSidebar
            knowledgeBases={myKnowledgeBases}
            onKnowledgeBasesChange={loadKnowledgeBases}
            onCreateClick={() => setIsCreateModalOpen(true)}
            onEditClick={handleEditKB}
            onDeleteClick={handleDeleteKB}
          />

          {/* Knowledge Square */}
          <section className={styles.hubMain}>
            {/* Title */}
            <h1 className={styles.hubTitle}>
              <span className={styles.hubTitleIcon}>✨</span>
              知识广场
              <span className={styles.hubTitleIcon}>✨</span>
            </h1>

            {/* Search */}
            <div className={styles.searchWrap}>
              <Search size={18} className={styles.searchIcon} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    loadPublicKBs();
                  }
                }}
                className={styles.search}
                placeholder="试试搜索感兴趣的知识库"
              />
            </div>

            {/* Category Tags */}
            <div className={styles.tags}>
              <button
                className={`${styles.tag} ${activeCategory === '2025精选' ? styles.tagActive : ''}`}
                onClick={() => handleCategoryClick('2025精选')}
              >
                🔥 2025精选
              </button>
              
              {DEFAULT_CATEGORIES.map(cat => {
                const Icon = CATEGORY_ICONS[cat];
                return (
                  <button
                    key={cat}
                    className={`${styles.tag} ${activeCategory === cat ? styles.tagActive : ''}`}
                    onClick={() => handleCategoryClick(cat)}
                  >
                    {Icon && <Icon size={14} />} {cat}
                  </button>
                );
              })}
              
              <button 
                className={styles.tag}
                onClick={() => setExpandedCategories(!expandedCategories)}
              >
                更多 {expandedCategories ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            </div>

            {/* Expanded Categories */}
            {expandedCategories && (
              <div className={styles.expandedCategories}>
                {hiddenCategories.map(cat => {
                  const Icon = CATEGORY_ICONS[cat];
                  return (
                    <button 
                      key={cat} 
                      className={`${styles.tag} ${activeCategory === cat ? styles.tagActive : ''}`}
                      onClick={() => handleCategoryClick(cat)}
                    >
                      {Icon && <Icon size={14} />} {cat}
                    </button>
                  );
                })}
              </div>
            )}

            {/* Knowledge Base List */}
            <div className={styles.feed}>
              {loading ? (
                <div className={styles.loadingState}>加载中...</div>
              ) : publicKbs.length === 0 ? (
                <div className={styles.emptyState}>
                  <div className={styles.emptyIcon}>📚</div>
                  <div className={styles.emptyText}>暂无公开知识库</div>
                  <div className={styles.emptyHint}>快去创建并公开你的第一个知识库吧</div>
                </div>
              ) : (
                publicKbs.map(kb => {
                  const CategoryIcon = CATEGORY_ICONS[kb.category];
                  return (
                    <div 
                      key={kb.id} 
                      className={styles.feedItem}
                      onClick={() => handleKBClick(kb.id)}
                      role="button"
                      tabIndex={0}
                    >
                      <div className={styles.feedIcon}>
                        <img src={kb.avatar} alt={kb.name} className={styles.kbAvatar} />
                      </div>
                      <div className={styles.feedBody}>
                        <div className={styles.feedHeader}>
                          <div className={styles.feedTitle}>{kb.name}</div>
                          {CategoryIcon && (
                            <div className={styles.categoryBadge}>
                              <CategoryIcon size={12} />
                              <span>{kb.category}</span>
                            </div>
                          )}
                        </div>
                        <div className={styles.feedDesc}>{kb.description || '暂无描述'}</div>
                        <div className={styles.feedMeta}>
                          <span className={styles.metaChip}>
                            <Users size={12} /> {kb.subscribersCount || 0} 订阅
                          </span>
                          <span className={styles.metaChip}>
                            <Database size={12} /> {kb.contents || 0} 文档
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

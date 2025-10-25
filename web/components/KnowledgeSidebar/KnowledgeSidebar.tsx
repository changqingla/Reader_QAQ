/**
 * 知识库侧边栏组件
 * 显示"我的知识库"和"订阅的知识库"列表
 */
import React, { useEffect, useState } from 'react';
import { Plus, Database, MoreVertical, Edit2, Trash2 } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { kbAPI } from '@/lib/api';
import { useToast } from '@/hooks/useToast';
import styles from './KnowledgeSidebar.module.css';

interface KnowledgeSidebarProps {
  knowledgeBases: any[];
  onKnowledgeBasesChange: () => void;
  onCreateClick: () => void;
  onEditClick?: (kb: any) => void;
  onDeleteClick?: (kbId: string) => void;
}

export default function KnowledgeSidebar({
  knowledgeBases,
  onKnowledgeBasesChange,
  onCreateClick,
  onEditClick,
  onDeleteClick
}: KnowledgeSidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const [menuOpen, setMenuOpen] = useState<string | null>(null);
  const [subscriptions, setSubscriptions] = useState<any[]>([]);

  useEffect(() => {
    loadSubscriptions();
  }, []);

  const loadSubscriptions = async () => {
    try {
      const response = await kbAPI.listSubscriptions();
      setSubscriptions(response.items);
    } catch (error) {
      console.error('Failed to load subscriptions:', error);
    }
  };

  const handleKBClick = (kbId: string) => {
    navigate(`/knowledge/${kbId}`);
    setMenuOpen(null);
  };

  const handleMenuClick = (e: React.MouseEvent, kbId: string) => {
    e.stopPropagation();
    setMenuOpen(menuOpen === kbId ? null : kbId);
  };

  const handleEdit = (e: React.MouseEvent, kb: any) => {
    e.stopPropagation();
    setMenuOpen(null);
    if (onEditClick) {
      onEditClick(kb);
    }
  };

  const handleDelete = (e: React.MouseEvent, kbId: string) => {
    e.stopPropagation();
    setMenuOpen(null);
    if (onDeleteClick) {
      onDeleteClick(kbId);
    }
  };

  const isActive = (kbId: string) => {
    return location.pathname === `/knowledge/${kbId}`;
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3 className={styles.sectionTitle}>我的知识库</h3>
          <button className={styles.addBtn} onClick={onCreateClick} title="新建知识库">
            <Plus size={16} />
          </button>
        </div>

        <div className={styles.list}>
          {knowledgeBases.length === 0 ? (
            <div className={styles.empty}>
              <Database size={24} className={styles.emptyIcon} />
              <p className={styles.emptyText}>还没有知识库</p>
              <button className={styles.emptyBtn} onClick={onCreateClick}>
                创建第一个
              </button>
            </div>
          ) : (
            knowledgeBases.map((kb) => (
              <div
                key={kb.id}
                className={`${styles.item} ${isActive(kb.id) ? styles.active : ''}`}
                onClick={() => handleKBClick(kb.id)}
              >
                <img src={kb.avatar} alt={kb.name} className={styles.avatar} />
                <div className={styles.itemBody}>
                  <div className={styles.itemName}>{kb.name}</div>
                  <div className={styles.itemMeta}>{kb.contents || 0} 文档</div>
                </div>
                <button
                  className={styles.menuBtn}
                  onClick={(e) => handleMenuClick(e, kb.id)}
                >
                  <MoreVertical size={14} />
                </button>

                {menuOpen === kb.id && (
                  <div className={styles.menu}>
                    <button className={styles.menuItem} onClick={(e) => handleEdit(e, kb)}>
                      <Edit2 size={14} />
                      <span>编辑</span>
                    </button>
                    <button
                      className={`${styles.menuItem} ${styles.danger}`}
                      onClick={(e) => handleDelete(e, kb.id)}
                    >
                      <Trash2 size={14} />
                      <span>删除</span>
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {subscriptions.length > 0 && (
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h3 className={styles.sectionTitle}>订阅的知识库</h3>
          </div>

          <div className={styles.list}>
            {subscriptions.map((kb) => (
              <div
                key={kb.id}
                className={`${styles.item} ${isActive(kb.id) ? styles.active : ''}`}
                onClick={() => handleKBClick(kb.id)}
              >
                <img src={kb.avatar} alt={kb.name} className={styles.avatar} />
                <div className={styles.itemBody}>
                  <div className={styles.itemName}>{kb.name}</div>
                  <div className={styles.itemMeta}>{kb.contents || 0} 文档</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}



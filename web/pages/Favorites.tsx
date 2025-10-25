/**
 * 收藏页面
 * 显示用户收藏的知识库和文档
 */
import React, { useState, useEffect } from 'react';
import { Database, FileText, Trash2, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '@/components/Sidebar/Sidebar';
import { favoriteAPI, kbAPI } from '@/lib/api';
import { useToast } from '@/hooks/useToast';
import styles from './Favorites.module.css';

type TabType = 'kb' | 'doc';

export default function Favorites() {
  const navigate = useNavigate();
  const toast = useToast();
  const [activeTab, setActiveTab] = useState<TabType>('kb');
  const [favoriteKBs, setFavoriteKBs] = useState<any[]>([]);
  const [favoriteDocs, setFavoriteDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  useEffect(() => {
    loadFavorites();
  }, [activeTab]);

  const loadFavorites = async () => {
    setLoading(true);
    try {
      if (activeTab === 'kb') {
        const response = await favoriteAPI.listFavoriteKBs();
        setFavoriteKBs(response.items);
      } else {
        const response = await favoriteAPI.listFavoriteDocuments();
        setFavoriteDocs(response.items);
      }
    } catch (error: any) {
      console.error('Failed to load favorites:', error);
      toast.error(error.message || '加载收藏失败');
    } finally {
      setLoading(false);
    }
  };

  const handleUnfavoriteKB = async (kbId: string) => {
    try {
      await favoriteAPI.unfavoriteKB(kbId);
      toast.success('已取消收藏');
      loadFavorites();
    } catch (error: any) {
      toast.error(error.message || '操作失败');
    }
  };

  const handleUnfavoriteDoc = async (docId: string) => {
    try {
      await favoriteAPI.unfavoriteDocument(docId);
      toast.success('已取消收藏');
      loadFavorites();
    } catch (error: any) {
      toast.error(error.message || '操作失败');
    }
  };

  return (
    <div className={styles.page}>
      {isMobile && isSidebarOpen && (
        <div className={styles.overlay} onClick={() => setIsSidebarOpen(false)} />
      )}

      <div className={`${styles.sidebarContainer} ${isMobile && isSidebarOpen ? styles.open : ''}`}>
        <Sidebar 
          onNewChat={() => {}} 
          onSelectChat={() => {}} 
          selectedChatId={undefined} 
        />
      </div>
      
      <div className={styles.main}>
        <h1 className={styles.title}>我的收藏</h1>

        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${activeTab === 'kb' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('kb')}
          >
            <Database size={16} />
            收藏的知识库
          </button>
          <button
            className={`${styles.tab} ${activeTab === 'doc' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('doc')}
          >
            <FileText size={16} />
            收藏的文档
          </button>
        </div>

        {loading ? (
          <div className={styles.loading}>加载中...</div>
        ) : (
          <div className={styles.content}>
            {activeTab === 'kb' ? (
              favoriteKBs.length === 0 ? (
                <div className={styles.empty}>
                  <Database size={48} />
                  <p>还没有收藏任何知识库</p>
                </div>
              ) : (
                <div className={styles.grid}>
                  {favoriteKBs.map((kb) => (
                    <div key={kb.id} className={styles.card}>
                      <img src={kb.avatar} alt={kb.name} className={styles.avatar} />
                      <div className={styles.cardBody}>
                        <h3 className={styles.cardTitle}>{kb.name}</h3>
                        <p className={styles.cardDesc}>{kb.description || '暂无描述'}</p>
                        <div className={styles.cardMeta}>
                          {kb.contents || 0} 文档
                        </div>
                        <div className={styles.cardActions}>
                          <button
                            className={styles.btnView}
                            onClick={() => navigate(`/knowledge/${kb.id}`)}
                          >
                            <ExternalLink size={14} />
                            查看
                          </button>
                          <button
                            className={styles.btnDelete}
                            onClick={() => handleUnfavoriteKB(kb.id)}
                            title="取消收藏"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )
            ) : (
              favoriteDocs.length === 0 ? (
                <div className={styles.empty}>
                  <FileText size={48} />
                  <p>还没有收藏任何文档</p>
                </div>
              ) : (
                <div className={styles.list}>
                  {favoriteDocs.map((doc) => (
                    <div key={doc.id} className={styles.docItem}>
                      <FileText size={20} />
                      <div className={styles.docInfo}>
                        <div className={styles.docName}>{doc.name}</div>
                        <div className={styles.docKb}>来自: {doc.kbName}</div>
                      </div>
                      <button
                        className={styles.btnDelete}
                        onClick={() => handleUnfavoriteDoc(doc.id)}
                        title="取消收藏"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * 收藏页面
 * 显示用户收藏的知识库和文档，支持PDF文档预览
 */
import React, { useState, useEffect } from 'react';
import { Database, FileText, Trash2, ExternalLink, X, Loader2, Star, MessageCircle, Send, User, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '@/components/Sidebar/Sidebar';
import OptimizedMarkdown from '@/components/OptimizedMarkdown';
import { api, favoriteAPI, kbAPI } from '@/lib/api';
import { useToast } from '@/hooks/useToast';
import { useRAGChat } from '@/hooks/useRAGChat';
import { useChatSessions } from '@/hooks/useChatSessions';
import styles from './Favorites.module.css';

type TabType = 'kb' | 'doc';

export default function Favorites() {
  const navigate = useNavigate();
  const toast = useToast();
  const { chatSessions, refreshSessions } = useChatSessions();
  const [activeTab, setActiveTab] = useState<TabType>('kb');
  const [favoriteKBs, setFavoriteKBs] = useState<any[]>([]);
  const [favoriteDocs, setFavoriteDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  
  // Preview State
  const [previewDoc, setPreviewDoc] = useState<any>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [loadingPreview, setLoadingPreview] = useState(false);
  
  // RAG Chat Hook - 当预览文档时使用
  const { messages, isStreaming, sendMessage, clearMessages } = useRAGChat({
    kbId: previewDoc?.kbId,
    docIds: previewDoc ? [previewDoc.id] : undefined,
    mode: 'deep',
    onError: (error) => toast.error(`对话错误: ${error}`)
  });
  
  const [inputMessage, setInputMessage] = useState('');

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
    console.log('handleUnfavoriteKB called with kbId:', kbId);
    try {
      await favoriteAPI.unfavoriteKB(kbId);
      console.log('unfavoriteKB API call successful');
      toast.success('已取消收藏');
      loadFavorites();
    } catch (error: any) {
      console.error('unfavoriteKB error:', error);
      toast.error(error.message || '操作失败');
    }
  };

  const handleUnfavoriteDoc = async (docId: string) => {
    console.log('handleUnfavoriteDoc called with docId:', docId);
    try {
      await favoriteAPI.unfavoriteDocument(docId);
      console.log('unfavoriteDocument API call successful');
      toast.success('已取消收藏');
      // 如果当前正在预览这个文档，关闭预览
      if (previewDoc?.id === docId) {
        handleClosePreview();
      }
      loadFavorites();
    } catch (error: any) {
      console.error('unfavoriteDocument error:', error);
      toast.error(error.message || '操作失败');
    }
  };

  // 预览文档
  const handlePreviewDocument = async (doc: any) => {
    setLoadingPreview(true);
    clearMessages(); // 清空对话历史
    try {
      const response = await kbAPI.getDocumentUrl(doc.kbId, doc.id);
      setPreviewDoc(doc);
      setPreviewUrl(response.url);
    } catch (error: any) {
      toast.error(error.message || '无法加载文档预览');
      setPreviewDoc(null);
    } finally {
      setLoadingPreview(false);
    }
  };

  // 关闭预览
  const handleClosePreview = () => {
    setPreviewDoc(null);
    setPreviewUrl('');
    clearMessages();
    setInputMessage('');
  };

  // 发送消息
  const handleSendMessage = () => {
    if (!inputMessage.trim() || !previewDoc || isStreaming) return;
    sendMessage(inputMessage);
    setInputMessage('');
  };

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
      
      <div className={styles.main}>
        {previewDoc && activeTab === 'doc' ? (
          /* 预览模式：PDF预览 + 对话界面 */
          <div className={styles.previewMode}>
            {/* 左侧 PDF 预览 - 50% */}
            <div className={styles.pdfPreviewSection}>
              <div className={styles.previewHeader}>
                <div className={styles.previewTitle}>
                  <FileText size={16} />
                  {previewDoc.name}
                </div>
                <div className={styles.previewActions}>
                  <button 
                    className={styles.favoriteBtn}
                    title="已收藏"
                  >
                    <Star size={16} fill="#f59e0b" color="#f59e0b" />
                  </button>
                  <button className={styles.closeBtn} onClick={handleClosePreview}>
                    <X size={18} />
                    关闭预览
                  </button>
                </div>
              </div>
              <div className={styles.previewContent}>
                {loadingPreview ? (
                  <div className={styles.previewLoading}>
                    <Loader2 size={32} className="animate-spin" />
                    <p>加载中...</p>
                  </div>
                ) : (
                  <iframe
                    src={`${previewUrl}#toolbar=0&navpanes=0&scrollbar=1&view=FitH&zoom=page-width`}
                    className={styles.previewFrame}
                    title={previewDoc.name}
                  />
                )}
              </div>
            </div>

            {/* 右侧对话界面 - 50% */}
            <div className={styles.chatSectionFull}>
              <div className={styles.chatHeader}>
                <MessageCircle size={18} />
                <span>文档对话</span>
              </div>
              <div className={styles.chatMessages}>
                {messages.length === 0 ? (
                  <div className={styles.chatEmpty}>
                    <MessageCircle size={56} />
                    <p>开始与文档对话</p>
                    <span>提出你的问题，AI 将基于文档内容回答</span>
                  </div>
                ) : (
                  <>
                    {messages.map((msg, index) => (
                      <div 
                        key={msg.id} 
                        className={`${styles.messageItem} ${msg.role === 'user' ? styles.userMessageItem : styles.aiMessageItem}`}
                      >
                        <div className={msg.role === 'user' ? styles.userAvatar : styles.aiAvatar}>
                          {msg.role === 'user' ? <User size={16} /> : <Sparkles size={16} />}
                        </div>
                        <div className={styles.messageContentWrapper}>
                          {msg.role === 'assistant' && !msg.content && isStreaming && index === messages.length - 1 ? (
                            <div className={styles.thinking}>
                              <div className={styles.thinkingDots}>
                                <span className={styles.dot}></span>
                                <span className={styles.dot}></span>
                                <span className={styles.dot}></span>
                              </div>
                              <span className={styles.thinkingText}>正在思考...</span>
                            </div>
                          ) : (
                            <>
                              <div className={msg.role === 'user' ? styles.userMessageText : styles.aiMessageText}>
                                {msg.role === 'user' ? (
                                  msg.content
                                ) : (
                                  <OptimizedMarkdown>
                                    {msg.content}
                                  </OptimizedMarkdown>
                                )}
                              </div>
                              {msg.quotes && msg.quotes.length > 0 && (
                                <div className={styles.quotes}>
                                  {msg.quotes.map((quote: any, i: number) => (
                                    <div key={i} className={styles.quoteCard}>
                                      <div className={styles.quoteSource}>📄 {quote.source}</div>
                                      {quote.page && (
                                        <div className={styles.quotePage}>第 {quote.page} 页</div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </>
                )}
              </div>
              <div className={styles.chatInputArea}>
                <div className={styles.chatInputWrap}>
                  <input
                    type="text"
                    placeholder="输入你的问题..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !isStreaming && inputMessage.trim() && handleSendMessage()}
                    className={styles.chatInput}
                    disabled={isStreaming}
                  />
                  <button 
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isStreaming}
                    className={styles.sendBtn}
                  >
                    <Send size={18} />
                  </button>
                </div>
                <div className={styles.chatFooter}>
                  答案由AI生成，AI也会犯错。
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* 列表模式：显示我的收藏 */
          <div className={styles.contentArea}>
            {/* 左侧列表区域 */}
            <div className={styles.listSection}>
            <div className={styles.header}>
              <h1 className={styles.title}>
                <Star size={24} className={styles.titleIcon} />
                我的收藏
              </h1>
            </div>

            <div className={styles.tabs}>
              <button
                className={`${styles.tab} ${activeTab === 'kb' ? styles.tabActive : ''}`}
                onClick={() => {
                  setActiveTab('kb');
                  handleClosePreview();
                }}
              >
                <Database size={16} />
                知识库
              </button>
              <button
                className={`${styles.tab} ${activeTab === 'doc' ? styles.tabActive : ''}`}
                onClick={() => setActiveTab('doc')}
              >
                <FileText size={16} />
                文档
              </button>
            </div>

            {loading ? (
              <div className={styles.loading}>
                <Loader2 size={24} className="animate-spin" />
                <p>加载中...</p>
              </div>
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
                          <div className={styles.cardHeader}>
                            <img src={kb.avatar} alt={kb.name} className={styles.avatar} />
                            <div className={styles.favoriteIcon}>
                              <Star size={16} fill="#f59e0b" color="#f59e0b" />
                            </div>
                          </div>
                          <div className={styles.cardBody}>
                            <h3 className={styles.cardTitle}>{kb.name}</h3>
                            <p className={styles.cardDesc}>{kb.description || '暂无描述'}</p>
                            <div className={styles.cardMeta}>
                              <FileText size={12} />
                              {kb.contents || 0} 文档
                            </div>
                          </div>
                          <div className={styles.cardActions}>
                            <button
                              className={styles.btnView}
                              onClick={() => navigate(`/knowledge/${kb.id}`)}
                            >
                              <ExternalLink size={14} />
                              查看详情
                            </button>
                            <button
                              className={styles.btnUnfavorite}
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                handleUnfavoriteKB(kb.id);
                              }}
                              onMouseDown={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                              }}
                              title="取消收藏"
                            >
                              <Trash2 size={14} />
                            </button>
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
                    <div className={styles.docList}>
                      {favoriteDocs.map((doc) => (
                        <div 
                          key={doc.id} 
                          className={`${styles.docItem} ${previewDoc?.id === doc.id ? styles.docItemActive : ''}`}
                        >
                          <div 
                            className={styles.docClickArea}
                            onClick={() => handlePreviewDocument(doc)}
                          >
                            <FileText size={20} className={styles.docIcon} />
                            <div className={styles.docInfo}>
                              <div className={styles.docName}>{doc.name}</div>
                              <div className={styles.docKb}>
                                <Database size={12} />
                                {doc.kbName}
                              </div>
                            </div>
                          </div>
                          <button
                            className={styles.btnFavorite}
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              console.log('Star clicked! Unfavoriting docId:', doc.id);
                              handleUnfavoriteDoc(doc.id);
                            }}
                            onMouseDown={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                            }}
                            title="取消收藏"
                          >
                            <Star size={18} fill="#f59e0b" color="#f59e0b" />
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
        )}
      </div>
    </div>
  );
}

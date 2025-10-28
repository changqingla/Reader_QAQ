/**
 * 知识库详情页
 * 支持：公开/私有切换、订阅、文档收藏、文档管理
 */
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '@/components/Sidebar/Sidebar';
import OptimizedMarkdown from '@/components/OptimizedMarkdown';
import KnowledgeSidebar, { KnowledgeSidebarRef } from '@/components/KnowledgeSidebar/KnowledgeSidebar';
import CreateKnowledgeModal from '@/components/CreateKnowledgeModal/CreateKnowledgeModal';
import EditKnowledgeModal from '@/components/EditKnowledgeModal/EditKnowledgeModal';
import ConfirmModal from '@/components/ConfirmModal/ConfirmModal';
import { kbAPI, favoriteAPI, api } from '@/lib/api';
import { useToast } from '@/hooks/useToast';
import { useRAGChat } from '@/hooks/useRAGChat';
import { 
  Upload, 
  FileText, 
  Globe,
  GlobeLock,
  Users,
  User,
  UserPlus,
  UserMinus,
  Sparkles,
  Star,
  Send,
  MessageCircle,
  Loader2,
  X,
  Settings,
  Trash2
} from 'lucide-react';
import styles from './KnowledgeDetail.module.css';

export default function KnowledgeDetail() {
  const { kbId } = useParams<{ kbId: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  
  // UI State
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isMainSidebarCollapsed, setIsMainSidebarCollapsed] = useState(false);
  
  // Modal State
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isTogglePublicModalOpen, setIsTogglePublicModalOpen] = useState(false);
  const [isUnsubscribeModalOpen, setIsUnsubscribeModalOpen] = useState(false);
  
  // Data State
  const [myKnowledgeBases, setMyKnowledgeBases] = useState<any[]>([]);
  const [currentKb, setCurrentKb] = useState<any>(null);
  const [documents, setDocuments] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [quota, setQuota] = useState({ usedBytes: 0, limitBytes: 500000000000 });
  
  // Favorite State
  const [favoriteDocIds, setFavoriteDocIds] = useState<Set<string>>(new Set());
  
  // Chat State
  const [chatInput, setChatInput] = useState('');
  const [chatSessions, setChatSessions] = useState<any[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>(undefined);
  
  // RAG Chat Hook - 知识库页面固定使用 deep 模式
  const { messages, isStreaming, sendMessage, clearMessages } = useRAGChat({
    kbId: kbId,
    sessionId: currentSessionId,
    mode: 'deep',
    onError: (error) => toast.error(`对话错误: ${error}`),
    onSessionCreated: (newSessionId) => {
      setCurrentSessionId(newSessionId);
      loadChatSessions();
    }
  });
  
  // PDF Preview State
  const [previewDoc, setPreviewDoc] = useState<any>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [loadingPreview, setLoadingPreview] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const kbSidebarRef = useRef<KnowledgeSidebarRef>(null);

  // 加载聊天会话列表
  const loadChatSessions = async () => {
    try {
      const response = await api.listChatSessions(1, 50);
      setChatSessions(response.sessions);
    } catch (error) {
      console.error('Failed to load chat sessions:', error);
    }
  };

  // 格式化相对时间
  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    
    // 超过7天显示具体日期
    return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' });
  };

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  useEffect(() => {
    loadKnowledgeBases();
    loadQuota();
    loadChatSessions();
  }, []);

  useEffect(() => {
    if (kbId) {
      loadCurrentKB();
      loadDocuments();
    }
  }, [kbId]);

  const loadKnowledgeBases = async () => {
    try {
      const response = await kbAPI.listKnowledgeBases();
      setMyKnowledgeBases(response.items);
    } catch (error: any) {
      console.error('Failed to load knowledge bases:', error);
      toast.error(error.message || '加载知识库失败');
    }
  };

  const loadCurrentKB = async () => {
    if (!kbId) return;
    try {
      // 使用 getKnowledgeBaseInfo 支持公开和私有知识库
      const kb = await kbAPI.getKnowledgeBaseInfo(kbId);
      setCurrentKb(kb);
    } catch (error: any) {
      console.error('Failed to load current KB:', error);
      toast.error(error.message || '无法访问该知识库');
      navigate('/knowledge');
    }
  };

  const loadQuota = async () => {
    try {
      const response = await kbAPI.getQuota();
      setQuota(response);
    } catch (error) {
      console.error('Failed to load quota:', error);
    }
  };

  const loadDocuments = async () => {
    if (!kbId) return;
    
    try {
      const response = await kbAPI.listDocuments(kbId);
      setDocuments(response.items);
    } catch (error: any) {
      console.error('Failed to load documents:', error);
      toast.error(error.message || '加载文档失败');
    }
  };

  // ============ File Upload Handlers ============

  const handleDragEnter: React.DragEventHandler<HTMLDivElement> = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (currentKb?.isOwner) setIsDragging(true);
  };

  const handleDragLeave: React.DragEventHandler<HTMLDivElement> = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop: React.DragEventHandler<HTMLDivElement> = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (!currentKb?.isOwner) {
      toast.warning('只有所有者可以上传文档');
      return;
    }
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await handleFilesUpload(Array.from(e.dataTransfer.files));
    }
  };

  const handleOpenPicker = () => fileInputRef.current?.click();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await handleFilesUpload(Array.from(e.target.files));
      e.target.value = '';
    }
  };

  const handleFilesUpload = async (files: File[]) => {
    if (!kbId) {
      toast.warning('请先选择一个知识库');
      return;
    }

    if (!currentKb?.isOwner) {
      toast.warning('只有所有者可以上传文档');
      return;
    }

    setUploading(true);
    try {
      for (const file of files) {
        await kbAPI.uploadDocument(kbId, file);
      }
      await loadDocuments();
      await loadQuota();
      toast.success('文档上传成功！');
    } catch (error: any) {
      toast.error(error.message || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!kbId) return;
    if (!currentKb?.isOwner) {
      toast.warning('只有所有者可以删除文档');
      return;
    }

    setIsDeleteModalOpen(true);
    // Store docId for confirmation
    (window as any).__pendingDeleteDocId = docId;
  };

  const confirmDeleteDocument = async () => {
    const docId = (window as any).__pendingDeleteDocId;
    if (!docId || !kbId) return;

    try {
      await kbAPI.deleteDocument(kbId, docId);
      await loadDocuments();
      await loadQuota();
      toast.success('文档已删除');
    } catch (error: any) {
      toast.error(error.message || '删除失败');
    } finally {
      setIsDeleteModalOpen(false);
      delete (window as any).__pendingDeleteDocId;
    }
  };

  // ============ Knowledge Base Management ============

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
    setIsEditModalOpen(true);
  };

  const handleSaveKB = async (data: { name: string; description: string; category: string }) => {
    if (!kbId) return;
    try {
      await kbAPI.updateKnowledgeBase(kbId, data);
      await loadCurrentKB();
      await loadKnowledgeBases();
      toast.success('知识库已更新');
    } catch (error: any) {
      toast.error(error.message || '更新知识库失败');
    }
  };

  const handleDeleteKB = async () => {
    if (!kbId) return;
    try {
      await kbAPI.deleteKnowledgeBase(kbId);
      toast.success('知识库已删除');
      navigate('/knowledge');
    } catch (error: any) {
      toast.error(error.message || '删除知识库失败');
    }
  };

  // ============ Public/Private Toggle ============

  const handleTogglePublic = () => {
    setIsTogglePublicModalOpen(true);
  };

  const confirmTogglePublic = async () => {
    if (!kbId) return;
    try {
      const result = await kbAPI.togglePublic(kbId);
      await loadCurrentKB();
      const message = result.isPublic 
        ? '知识库已公开到知识广场！' 
        : '知识库已设为私有';
      toast.success(message);
    } catch (error: any) {
      toast.error(error.message || '操作失败');
    } finally {
      setIsTogglePublicModalOpen(false);
    }
  };

  // ============ Subscribe/Unsubscribe ============

  const handleSubscribe = async () => {
    if (!kbId) return;
    if (currentKb?.isSubscribed) {
      setIsUnsubscribeModalOpen(true);
    } else {
      try {
        await kbAPI.subscribe(kbId);
        await loadCurrentKB();
        // 刷新侧边栏的订阅列表
        await kbSidebarRef.current?.refreshSubscriptions();
        toast.success('订阅成功！');
      } catch (error: any) {
        toast.error(error.message || '操作失败');
      }
    }
  };

  const confirmUnsubscribe = async () => {
    if (!kbId) return;
    try {
      await kbAPI.unsubscribe(kbId);
      await loadCurrentKB();
      // 刷新侧边栏的订阅列表
      await kbSidebarRef.current?.refreshSubscriptions();
      toast.success('已取消订阅');
    } catch (error: any) {
      toast.error(error.message || '操作失败');
    } finally {
      setIsUnsubscribeModalOpen(false);
    }
  };

  // ============ PDF Preview ============

  const handlePreviewDocument = async (doc: any) => {
    if (!kbId) return;
    
    setLoadingPreview(true);
    setPreviewDoc(doc);
    setIsMainSidebarCollapsed(true); // 自动折叠主侧边栏
    
    try {
      const response = await kbAPI.getDocumentUrl(kbId, doc.id);
      setPreviewUrl(response.url);
    } catch (error: any) {
      toast.error(error.message || '无法加载文档预览');
      setPreviewDoc(null);
      setIsMainSidebarCollapsed(false); // 如果失败，恢复侧边栏
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleClosePreview = () => {
    setPreviewDoc(null);
    setPreviewUrl('');
    setIsMainSidebarCollapsed(false); // 恢复主侧边栏
  };

  // ============ Favorite Document ============

  const handleToggleFavoriteDoc = async (docId: string) => {
    if (!kbId) return;
    
    try {
      if (favoriteDocIds.has(docId)) {
        await favoriteAPI.unfavoriteDocument(docId);
        setFavoriteDocIds(prev => {
          const next = new Set(prev);
          next.delete(docId);
          return next;
        });
        toast.success('已取消收藏');
      } else {
        await favoriteAPI.favoriteDocument(docId, kbId);
        setFavoriteDocIds(prev => new Set(prev).add(docId));
        toast.success('已收藏');
      }
    } catch (error: any) {
      toast.error(error.message || '操作失败');
    }
  };

  // ============ Utilities ============

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
  };

  return (
    <div className={styles.page}>
      {isMobile && isSidebarOpen && (
        <div className={styles.overlay} onClick={() => setIsSidebarOpen(false)} />
      )}

      <div className={`${styles.sidebarContainer} ${isMobile && isSidebarOpen ? styles.open : ''}`}>
        <Sidebar 
          onNewChat={() => {
            setCurrentSessionId(undefined);
            clearMessages();
          }} 
          onSelectChat={(chatId) => {
            if (chatId !== currentSessionId) {
              setCurrentSessionId(chatId);
            }
          }} 
          onDeleteChat={async (chatId) => {
            try {
              await api.deleteChatSession(chatId);
              if (chatId === currentSessionId) {
                setCurrentSessionId(undefined);
                clearMessages();
              }
              await loadChatSessions();
              toast.success('对话已删除');
            } catch (error) {
              console.error('Failed to delete chat:', error);
              toast.error('删除对话失败');
            }
          }}
          selectedChatId={currentSessionId}
          chats={chatSessions}
          collapsed={isMainSidebarCollapsed}
          onToggleCollapse={() => setIsMainSidebarCollapsed(!isMainSidebarCollapsed)}
        />
      </div>

      {/* Modals */}
      <CreateKnowledgeModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateKB}
      />

      {currentKb && (
        <EditKnowledgeModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          onSave={handleSaveKB}
          initialData={{
            name: currentKb.name,
            description: currentKb.description,
            category: currentKb.category || '其它'
          }}
        />
      )}

      <ConfirmModal
        isOpen={isTogglePublicModalOpen}
        title={currentKb?.isPublic ? "设为私有" : "公开知识库"}
        message={currentKb?.isPublic 
          ? "设为私有后，其他用户将无法访问此知识库。确定继续吗？"
          : "公开后，所有用户都可以查看并订阅此知识库。其他用户无法修改或删除内容。确定公开吗？"
        }
        type={currentKb?.isPublic ? "warning" : "info"}
        confirmText="确认"
        cancelText="取消"
        onConfirm={confirmTogglePublic}
        onCancel={() => setIsTogglePublicModalOpen(false)}
      />

      <ConfirmModal
        isOpen={isUnsubscribeModalOpen}
        title="取消订阅"
        message="确定要取消订阅此知识库吗？取消后将不再显示在「我的订阅」中。"
        type="warning"
        confirmText="确认取消订阅"
        cancelText="取消"
        onConfirm={confirmUnsubscribe}
        onCancel={() => setIsUnsubscribeModalOpen(false)}
      />

      <ConfirmModal
        isOpen={isDeleteModalOpen}
        title="删除文档"
        message="删除后无法恢复，确定要删除这个文档吗？"
        type="danger"
        confirmText="删除"
        cancelText="取消"
        onConfirm={confirmDeleteDocument}
        onCancel={() => setIsDeleteModalOpen(false)}
      />

      <div className={styles.main}>
        <div className={styles.contentArea}>
          {/* Knowledge Sidebar */}
          <KnowledgeSidebar
            ref={kbSidebarRef}
            knowledgeBases={myKnowledgeBases}
            onKnowledgeBasesChange={loadKnowledgeBases}
            onCreateClick={() => setIsCreateModalOpen(true)}
            onEditClick={handleEditKB}
            onDeleteClick={handleDeleteKB}
          />

          {/* Center - KB Info & Upload */}
          <main className={styles.uploadSection}>
            {/* KB Info Card */}
            <div className={styles.kbInfoCard}>
              <div className={styles.kbHeader}>
                <div className={styles.kbInfo}>
                  <img 
                    src={currentKb?.avatar || '/kb.png'} 
                    alt={currentKb?.name || 'KB'} 
                    className={styles.kbAvatar}
                  />
                  <div className={styles.kbDetails}>
                    <div className={styles.kbTitle}>{currentKb?.name || '请选择知识库'}</div>
                    {currentKb?.description && (
                      <div className={styles.kbDescription}>{currentKb.description}</div>
                    )}
                    <div className={styles.kbMeta}>
                      <span>{currentKb?.contents || 0} 文档</span>
                      {currentKb?.isPublic && (
                        <>
                          <span>·</span>
                          <span><Users size={12} /> {currentKb.subscribersCount || 0} 订阅</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className={styles.kbActions}>
                  {currentKb?.isOwner ? (
                    <>
                      {/* 上传按钮 - 只在有文档时显示 */}
                      {documents.length > 0 && (
                        <button 
                          className={styles.iconBtn}
                          onClick={() => fileInputRef.current?.click()}
                          title="上传文件"
                          disabled={uploading}
                        >
                          <Upload size={18} />
                        </button>
                      )}
                      <button 
                        className={styles.iconBtn}
                        onClick={handleTogglePublic}
                        title={currentKb.isPublic ? "设为私有" : "公开知识库"}
                      >
                        {currentKb.isPublic ? <Globe size={18} /> : <GlobeLock size={18} />}
                      </button>
                      <button 
                        className={styles.iconBtn}
                        onClick={() => handleEditKB(currentKb)}
                        title="编辑知识库"
                      >
                        <Settings size={18} />
                      </button>
                    </>
                  ) : currentKb?.isPublic && (
                    <button 
                      className={`${styles.subscribeBtn} ${currentKb.isSubscribed ? styles.subscribed : ''}`}
                      onClick={handleSubscribe}
                    >
                      {currentKb.isSubscribed ? (
                        <><UserMinus size={16} /> 已订阅</>
                      ) : (
                        <><UserPlus size={16} /> 订阅</>
                      )}
                    </button>
                  )}
                </div>
              </div>

              {/* Hidden file input - always present */}
              {currentKb?.isOwner && (
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.md,.txt,.docx,.xlsx,.pptx"
                  onChange={handleFileChange}
                  className={styles.hiddenInput}
                  disabled={uploading}
                />
              )}

              {/* Upload Area - Only show when no documents */}
              {currentKb?.isOwner && documents.length === 0 && (
                <>
                  <div
                    className={`${styles.dropzone} ${isDragging ? styles.dropzoneActive : ''}`}
                    onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
                    onDragEnter={handleDragEnter}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                  >
                    <Upload size={60} strokeWidth={1.5} className={styles.uploadIcon} />
                    <div className={styles.dropTitle}>拖拽文件到这里上传</div>
                    <div className={styles.dropHint}>或点击下方按钮选择文件</div>
                  </div>

                  <div className={styles.fileTypeHint}>
                    上传pdf格式文件，单个文件最大 100MB
                  </div>

                  <div className={styles.uploadActions}>
                    <button 
                      className={styles.uploadButton} 
                      onClick={handleOpenPicker} 
                      disabled={uploading}
                    >
                      {uploading ? <><Loader2 size={16} className="animate-spin" /> 上传中...</> : '上传文件'}
                    </button>
                  </div>
                </>
              )}
            </div>

            {/* Document List - Flat design, not in card */}
            {documents.length > 0 && (
              <div className={styles.documentList}>
                  {documents.map((doc) => (
                    <div 
                      key={doc.id} 
                      className={`${styles.fileRow} ${previewDoc?.id === doc.id ? styles.fileRowActive : ''}`}
                    >
                      <FileText size={16} />
                      <div 
                        className={styles.fileInfo}
                        onClick={() => doc.status === 'ready' && handlePreviewDocument(doc)}
                        style={{ cursor: doc.status === 'ready' ? 'pointer' : 'default' }}
                      >
                        <span className={styles.fileName}>{doc.name}</span>
                        <span className={styles.fileStatus}>
                          {doc.status === 'ready' && `${doc.uploadedAt ? formatRelativeTime(doc.uploadedAt) : ''} · 点击预览`}
                          {doc.status === 'processing' && '处理中...'}
                          {doc.status === 'uploading' && '上传中...'}
                          {doc.status === 'chunking' && '分块中...'}
                          {doc.status === 'embedding' && '向量化中...'}
                          {doc.status === 'failed' && '处理失败'}
                        </span>
                      </div>
                      <div className={styles.fileActions}>
                        <button 
                          className={`${styles.iconBtn} ${favoriteDocIds.has(doc.id) ? styles.favorited : ''}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggleFavoriteDoc(doc.id);
                          }}
                          title={favoriteDocIds.has(doc.id) ? "取消收藏" : "收藏文档"}
                        >
                          <Star size={14} fill={favoriteDocIds.has(doc.id) ? 'currentColor' : 'none'} />
                        </button>
                        {currentKb?.isOwner && (
                          <button 
                            className={styles.removeBtn} 
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteDocument(doc.id);
                            }}
                            title="删除文档"
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </main>

          {/* Right - Preview/Chat Area */}
          <section className={styles.chatArea}>
            {previewDoc ? (
              // PDF Preview
              <div className={styles.previewContainer}>
                <div className={styles.previewHeader}>
                  <div className={styles.previewTitle}>
                    <FileText size={18} />
                    <span>{previewDoc.name}</span>
                  </div>
                  <div className={styles.previewActions}>
                    <button 
                      className={`${styles.favoriteBtn} ${favoriteDocIds.has(previewDoc.id) ? styles.favorited : ''}`}
                      onClick={() => handleToggleFavoriteDoc(previewDoc.id)}
                      title={favoriteDocIds.has(previewDoc.id) ? "取消收藏" : "收藏文档"}
                    >
                      <Star size={16} fill={favoriteDocIds.has(previewDoc.id) ? 'currentColor' : 'none'} />
                      <span>{favoriteDocIds.has(previewDoc.id) ? '已收藏' : '收藏'}</span>
                    </button>
                    <button 
                      className={styles.closePreviewBtn}
                      onClick={handleClosePreview}
                      title="关闭预览"
                    >
                      关闭预览
                    </button>
                  </div>
                </div>
                <div className={styles.previewContent}>
                  {loadingPreview ? (
                    <div className={styles.previewLoading}>
                      <Loader2 size={48} className="animate-spin" />
                      <p>加载文档中...</p>
                    </div>
                  ) : previewUrl ? (
                    <iframe 
                      src={`${previewUrl}#toolbar=0&navpanes=0&scrollbar=1&view=FitH&zoom=page-width`}
                      className={styles.previewFrame}
                      title={previewDoc.name}
                    />
                  ) : (
                    <div className={styles.previewError}>
                      <FileText size={48} />
                      <p>无法加载文档预览</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              // Chat Interface
              <div className={styles.chatContainer}>
                <div className={styles.chatHeader}>
                  <MessageCircle size={20} />
                  <span>提问本知识库</span>
                </div>

                <div className={styles.chatContent}>
                  {messages.length === 0 ? (
                    <div className={styles.chatEmpty}>
                      <MessageCircle size={48} className={styles.chatEmptyIcon} />
                      <p className={styles.chatEmptyText}>开始对话，探索知识库的内容</p>
                    </div>
                  ) : (
                    <div className={styles.chatMessages}>
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
                                        {quote.page && <div className={styles.quotePage}>第 {quote.page} 页</div>}
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className={styles.chatInputSection}>
                  <div className={styles.chatInputWrap}>
                    <input 
                      className={styles.chatInput} 
                      placeholder="可对本知识库进行提问..." 
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey && !isStreaming && chatInput.trim()) {
                          e.preventDefault();
                          sendMessage(chatInput);
                          setChatInput('');
                        }
                      }}
                      disabled={isStreaming}
                    />
                    <button 
                      className={styles.sendButton}
                      onClick={() => {
                        if (chatInput.trim() && !isStreaming) {
                          sendMessage(chatInput);
                          setChatInput('');
                        }
                      }}
                      disabled={!chatInput.trim() || isStreaming}
                    >
                      <Send size={18} />
                    </button>
                  </div>

                  <div className={styles.chatFooter}>
                    结果由 AI 大模型生成，请谨慎使用。
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
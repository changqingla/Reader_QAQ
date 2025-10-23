import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '@/components/Sidebar/Sidebar';
import CreateKnowledgeModal from '@/components/CreateKnowledgeModal/CreateKnowledgeModal';
import { kbAPI } from '@/lib/api';
import { 
  Upload, 
  FileText, 
  Sparkles, 
  Clock, 
  Globe, 
  Search,
  Database,
  Rss,
  X,
  Send,
  Plus,
  MessageCircle,
  ChevronDown,
  Folder,
  Loader2
} from 'lucide-react';
import styles from './KnowledgeDetail.module.css';

export default function KnowledgeDetail() {
  const { kbId } = useParams<{ kbId: string }>();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);
  const [isDragging, setIsDragging] = React.useState(false);
  const [askInput, setAskInput] = React.useState('');
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [myKnowledgeBases, setMyKnowledgeBases] = React.useState<any[]>([]);
  const [currentKb, setCurrentKb] = React.useState<any>(null);
  const [documents, setDocuments] = React.useState<any[]>([]);
  const [uploading, setUploading] = React.useState(false);
  const [quota, setQuota] = React.useState({ usedBytes: 0, limitBytes: 500000000000 });
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);
  
  React.useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  // Load knowledge bases and quota
  React.useEffect(() => {
    loadKnowledgeBases();
    loadQuota();
  }, []);

  // Load documents when kbId from URL changes
  React.useEffect(() => {
    if (kbId) {
      loadCurrentKB();
      loadDocuments();
    }
  }, [kbId]);

  const loadKnowledgeBases = async () => {
    try {
      const response = await kbAPI.listKnowledgeBases();
      setMyKnowledgeBases(response.items);
    } catch (error) {
      console.error('Failed to load knowledge bases:', error);
    }
  };

  const loadCurrentKB = async () => {
    if (!kbId) return;
    try {
      const kb = myKnowledgeBases.find(kb => kb.id === kbId);
      if (kb) {
        setCurrentKb(kb);
      } else {
        // KB not in list yet, fetch from myKnowledgeBases
        await loadKnowledgeBases();
      }
    } catch (error) {
      console.error('Failed to load current KB:', error);
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
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleDragEnter: React.DragEventHandler<HTMLDivElement> = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
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
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await handleFilesUpload(Array.from(e.dataTransfer.files));
    }
  };

  const handleOpenPicker = () => fileInputRef.current?.click();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await handleFilesUpload(Array.from(e.target.files));
      e.target.value = ''; // Reset input
    }
  };

  const handleFilesUpload = async (files: File[]) => {
    if (!kbId) {
      alert('请先选择一个知识库');
      return;
    }

    setUploading(true);
    try {
      for (const file of files) {
        await kbAPI.uploadDocument(kbId, file);
      }
      // Reload documents after upload
      await loadDocuments();
      await loadQuota();
    } catch (error: any) {
      alert(error.message || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!kbId) return;
    if (!confirm('确定要删除这个文档吗？')) return;

    try {
      await kbAPI.deleteDocument(kbId, docId);
      await loadDocuments();
      await loadQuota();
    } catch (error: any) {
      alert(error.message || '删除失败');
    }
  };

  const handleAddKnowledgeBase = async (data: { name: string; description: string; tags: string[] }) => {
    try {
      await kbAPI.createKnowledgeBase(data.name, data.description, data.tags);
      await loadKnowledgeBases();
    } catch (error: any) {
      alert(error.message || '创建知识库失败');
    }
  };

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

      {/* App Sidebar */}
      <div className={`${styles.sidebarContainer} ${isMobile && isSidebarOpen ? styles.open : ''}`}>
        <Sidebar onNewChat={() => {}} onSelectChat={() => {}} selectedChatId={undefined} />
      </div>

      {/* 新建知识库弹窗 */}
      <CreateKnowledgeModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleAddKnowledgeBase}
      />

      <div className={styles.main}>
        <div className={styles.contentArea}>
          {/* 二级侧栏 - 与 Knowledge 页面一致 */}
          <aside className={styles.subSidebar}>
            <div className={styles.subSearch}>
              <Search size={16} className={styles.subSearchIcon} />
              <input className={styles.subSearchInput} placeholder="搜索你的知识库" />
            </div>

            <div className={styles.storageRow}>
              <span>我的知识库</span>
              <button className={styles.addKbBtn} onClick={() => setIsModalOpen(true)} aria-label="新建知识库">
                <Plus size={14} />
              </button>
            </div>
            <div className={styles.myList}>
              {myKnowledgeBases.map((kb) => (
                <button 
                  key={kb.id}
                  className={kb.id === kbId ? styles.myItemActive : styles.myItem}
                  onClick={() => navigate(`/knowledge/${kb.id}`)}
                >
                  <span className={styles.myDot} />
                  {kb.name}
                </button>
              ))}
            </div>

            <div className={styles.sectionCollapse}>
              <button className={styles.collapseBtnSm}>
                <ChevronDown size={14} /> 订阅
              </button>
              <div className={styles.subscribeList}>
                <div className={styles.subItem}><Folder size={14} /> 知识库</div>
                <div className={styles.subItem}><Rss size={14} /> RSS</div>
              </div>
            </div>
          </aside>

          {/* Center - Upload Section (侧边栏宽度的1.5倍 = 390px) */}
          <main className={styles.uploadSection}>
            <div className={styles.uploadCard}>
              <div className={styles.kbTitle}>
                <Database size={20} />
                <span>{currentKb?.name || '请选择知识库'}</span>
              </div>
              {currentKb?.description && (
                <div className={styles.kbSubtitle}>{currentKb.description}</div>
              )}
              <div className={styles.kbMeta}>
                {currentKb?.contents || 0} 内容 · {formatBytes(quota.usedBytes)} / {formatBytes(quota.limitBytes)}
              </div>

              <div
                className={`${styles.dropzone} ${isDragging ? styles.dropzoneActive : ''}`}
                onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className={styles.illustration}>
                  {/* Cute bear illustration placeholder */}
                  <div className={styles.bearIllustration}>
                    <Upload size={80} strokeWidth={1.5} className={styles.uploadIllustration} />
                  </div>
                </div>
                <div className={styles.dropTitle}>快来搭建你的知识库吧</div>
              </div>

              <div className={styles.fileTypeHint}>
                支持 pdf、md、txt、ppt、pptx、xlsx、xls、docx、webp、png、jpg、jpeg、mobi、epub、csv、azw3 等，单个文件最大 100MB
              </div>

              <div className={styles.uploadActions}>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.md,.txt,.docx,.xlsx,.pptx"
                  onChange={handleFileChange}
                  className={styles.hiddenInput}
                  disabled={uploading || !kbId}
                />
                <button 
                  className={styles.uploadButton} 
                  onClick={handleOpenPicker} 
                  disabled={uploading || !kbId}
                  aria-label="上传文件"
                >
                  {uploading ? <><Loader2 size={16} className="animate-spin" /> 上传中...</> : '上传文件'}
                </button>
              </div>

              {documents.length > 0 && (
                <div className={styles.fileList}>
                  {documents.map((doc) => (
                    <div key={doc.id} className={styles.fileRow}>
                      <FileText size={16} />
                      <div className={styles.fileInfo}>
                        <span className={styles.fileName}>{doc.name}</span>
                        <span className={styles.fileStatus}>
                          {doc.status === 'ready' && `${doc.chunkCount} 个分块`}
                          {doc.status === 'processing' && '处理中...'}
                          {doc.status === 'uploading' && '上传中...'}
                          {doc.status === 'chunking' && '分块中...'}
                          {doc.status === 'embedding' && '向量化中...'}
                          {doc.status === 'failed' && '处理失败'}
                        </span>
                      </div>
                      <button 
                        className={styles.removeBtn} 
                        onClick={() => handleDeleteDocument(doc.id)}
                        title="删除文档"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </main>

          {/* Right - Chat Area (剩余的所有区域) */}
          <section className={styles.chatArea}>
            <div className={styles.chatContainer}>
              <div className={styles.chatHeader}>
                <MessageCircle size={20} />
                <span>提问本知识库</span>
              </div>

              <div className={styles.chatContent}>
                <div className={styles.chatEmpty}>
                  <Sparkles size={48} className={styles.chatEmptyIcon} />
                  <p className={styles.chatEmptyText}>开始对话，探索知识库的内容</p>
                </div>
              </div>

              <div className={styles.chatInputSection}>
                <div className={styles.quickChips}>
                  <button className={styles.quickChip}>
                    <Sparkles size={14} />
                    观点洞察
                  </button>
                  <button className={styles.quickChip}>
                    <Clock size={14} />
                    时间脉络
                  </button>
                  <button className={styles.quickChip}>
                    <Globe size={14} />
                    网页摘要
                  </button>
                </div>

                <div className={styles.chatInputWrap}>
                  <input 
                    className={styles.chatInput} 
                    placeholder="可对本知识库进行提问..." 
                    value={askInput}
                    onChange={(e) => setAskInput(e.target.value)}
                  />
                  <button className={styles.sendButton}>
                    <Send size={18} />
                  </button>
                </div>

                <div className={styles.chatFooter}>
                  结果由 AI 大模型生成，禁止上传涉密、违法内容，请谨慎使用。
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}



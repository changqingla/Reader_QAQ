import React from 'react';
import Sidebar from '@/components/Sidebar/Sidebar';
import CreateKnowledgeModal from '@/components/CreateKnowledgeModal/CreateKnowledgeModal';
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
  Folder
} from 'lucide-react';
import styles from './KnowledgeDetail.module.css';

export default function KnowledgeDetail() {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);
  const [files, setFiles] = React.useState<File[]>([]);
  const [isDragging, setIsDragging] = React.useState(false);
  const [askInput, setAskInput] = React.useState('');
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [myKnowledgeBases, setMyKnowledgeBases] = React.useState([
    { id: 'default', name: '默认知识库', description: '', tags: [] as string[] },
    { id: 'test', name: '测试', description: '', tags: [] as string[] }
  ]);
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);
  
  React.useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  const addFiles = (newFiles: FileList | null) => {
    if (!newFiles) return;
    const next = Array.from(newFiles);
    setFiles(prev => [...prev, ...next]);
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

  const handleDrop: React.DragEventHandler<HTMLDivElement> = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    addFiles(e.dataTransfer.files);
  };

  const handleOpenPicker = () => fileInputRef.current?.click();
  const removeFile = (idx: number) => setFiles(prev => prev.filter((_, i) => i !== idx));

  const handleAddKnowledgeBase = (data: { name: string; description: string; tags: string[] }) => {
    const newKb = {
      id: Date.now().toString(),
      name: data.name,
      description: data.description,
      tags: data.tags
    };
    setMyKnowledgeBases([...myKnowledgeBases, newKb]);
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
              {myKnowledgeBases.map((kb, index) => (
                <button 
                  key={kb.id}
                  className={index === 0 ? styles.myItemActive : styles.myItem}
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
                <span>默认知识库</span>
              </div>
              <div className={styles.kbSubtitle}>长圈、系统自动创建的默认知识库</div>
              <div className={styles.kbMeta}>0 内容</div>

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
                  onChange={(e) => addFiles(e.target.files)}
                  className={styles.hiddenInput}
                />
                <button className={styles.uploadButton} onClick={handleOpenPicker} aria-label="上传文件">
                  上传文件
                </button>
                <button className={styles.pluginButton} onClick={() => alert('示例：打开浏览器插件以添加网页（前端演示）')}>
                  <Globe size={16} />
                  用插件添加网页
                </button>
              </div>

              {files.length > 0 && (
                <div className={styles.fileList}>
                  {files.map((f, idx) => (
                    <div key={`${f.name}-${idx}`} className={styles.fileRow}>
                      <FileText size={16} />
                      <span className={styles.fileName}>{f.name}</span>
                      <span className={styles.fileSize}>{(f.size / 1024 / 1024).toFixed(2)}MB</span>
                      <button className={styles.removeBtn} onClick={() => removeFile(idx)}>
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



import React from 'react';
import Sidebar from '@/components/Sidebar/Sidebar';
import { 
  Search, 
  Plus, 
  ChevronDown, 
  Folder,
  Rss,
  MessageCircle,
  ArrowLeft,
  MoreVertical,
  Clock,
  FileText,
  Users,
  Database,
  Sparkles,
  Globe,
  Send
} from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import styles from './KnowledgeHubDetail.module.css';

interface Post {
  id: string;
  title: string;
  author: string;
  avatar: string;
  replies: number;
  date: string;
  preview?: string;
  hasImage?: boolean;
}

// 模拟帖子数据
const mockPosts: Post[] = [
  {
    id: '1',
    title: '笔记本科普与选购',
    author: '鹿鹿',
    avatar: '🦌',
    replies: 311,
    date: '10-20',
    preview: '笔记本电脑相关的内容，包含各种科普与选购指南。'
  },
  {
    id: '2',
    title: '谁大一买笔记本是二手游戏本？',
    author: '鹿鹿',
    avatar: '🦌',
    replies: 0,
    date: '10-20'
  },
  {
    id: '3',
    title: '史电脑是在线上好还是去实体店好呢？',
    author: '鹿鹿',
    avatar: '🦌',
    replies: 0,
    date: '10-20'
  },
  {
    id: '4',
    title: '「高静模式」的正确打开方式——机械革命星曜 IG Ultra RTX5060...',
    author: '鹿鹿',
    avatar: '🦌',
    replies: 0,
    date: '10-17',
    hasImage: true
  },
  {
    id: '5',
    title: '想买个游戏本，线上好还是线下买？',
    author: '鹿鹿',
    avatar: '🦌',
    replies: 0,
    date: '10-15'
  },
  {
    id: '6',
    title: '联想斗战者 7000R9-8940HX 16GB+1TB 9000在线下电脑城买的 最低能么讲价？',
    author: '鹿鹿',
    avatar: '🦌',
    replies: 0,
    date: '10-14'
  },
  {
    id: '7',
    title: '现在京东方旗舰不是机械+固态硬盘的电脑了？',
    author: '鹿鹿',
    avatar: '🦌',
    replies: 0,
    date: '10-11'
  },
  {
    id: '8',
    title: '求助大学生买笔记本电脑，还在纠结？',
    author: '鹿鹿',
    avatar: '🦌',
    replies: 0,
    date: '09-26'
  },
  {
    id: '9',
    title: '5893的联想16Pro潮玩低配版，16g+1t，r9-8945hx和5060，值不值得？',
    author: '鹿鹿',
    avatar: '🦌',
    replies: 0,
    date: '09-09'
  }
];

export default function KnowledgeHubDetail() {
  const navigate = useNavigate();
  const { hubId } = useParams();
  const [selectedChatId, setSelectedChatId] = React.useState<string | undefined>();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [askInput, setAskInput] = React.useState('');
  const [selectedPostId, setSelectedPostId] = React.useState<string | null>(null);

  React.useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  // 模拟知识库信息
  const hubInfo = {
    name: '笔记本科普与选购',
    icon: '💻',
    subscribers: 86,
    contents: 311
  };

  // 简单的文档内容映射（示例）
  const postContentById: Record<string, string> = {
    '1': '这是一篇关于笔记本科普与选购的文章内容示例。\n\n- 明确需求\n- 合理预算\n- 对比评测',
    '2': '关于是否购买二手游戏本的讨论与建议。\n\n- 核查机器来源\n- 检测硬件健康\n- 对比新机价格',
    '3': '线上 VS 线下购买电脑的优缺点分析。',
    '4': '高静模式设置与体验分享。',
    '5': '线上还是线下买游戏本？给出若干建议清单。',
    '6': '电脑城讲价技巧与注意事项。',
    '7': '关于配置命名与固态硬盘的近期变化记录。',
    '8': '大学生购机纠结指南：性能、重量与价格平衡。',
    '9': '联想16Pro配置与价格分析。'
  };

  const selectedPost = selectedPostId ? mockPosts.find(p => p.id === selectedPostId) : null;

  return (
    <div className={styles.page}>
      {isMobile && isSidebarOpen && (
        <div className={styles.overlay} onClick={() => setIsSidebarOpen(false)} />
      )}

      {/* App Sidebar */}
      <div className={`${styles.sidebarContainer} ${isMobile && isSidebarOpen ? styles.open : ''}`}>
        <Sidebar 
          onNewChat={() => setSelectedChatId(undefined)} 
          onSelectChat={(id) => setSelectedChatId(id)} 
          selectedChatId={selectedChatId} 
        />
      </div>

      <div className={styles.main}>
        <div className={styles.contentArea}>
          {/* 左侧侧边栏 */}
          <aside className={styles.subSidebar}>
            <button className={styles.backBtn} onClick={() => navigate('/knowledge')}>
              <ArrowLeft size={16} />
              <span>返回</span>
            </button>

            <div className={styles.subSearch}>
              <Search size={16} className={styles.subSearchIcon} />
              <input 
                className={styles.subSearchInput} 
                placeholder="搜索你的知识库" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className={styles.storageRow}>
              <span>我的知识库</span>
              <button className={styles.addKbBtn} aria-label="新建知识库">
                <Plus size={14} />
              </button>
            </div>

            <div className={styles.myList}>
              <button className={styles.myItem}>
                <span className={styles.myDot} />默认知识库
              </button>
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

          {/* 中间内容区 */}
          <main className={styles.hubContent}>
            {/* 知识库头部 */}
            <div className={styles.hubHeader}>
              <div className={styles.hubIcon}>{hubInfo.icon}</div>
              <div className={styles.hubInfo}>
                <h1 className={styles.hubTitle}>{hubInfo.name}</h1>
                <div className={styles.hubMeta}>
                  <span className={styles.metaItem}>
                    <Users size={14} />
                    {hubInfo.subscribers} 订阅
                  </span>
                  <span className={styles.metaDot}>•</span>
                  <span className={styles.metaItem}>
                    <Database size={14} />
                    {hubInfo.contents} 内容
                  </span>
                </div>
              </div>
              <button className={styles.subscribeBtn}>+ 订阅知识库</button>
            </div>

            {/* 帖子列表 */}
            <div className={styles.postsList}>
              {mockPosts.map(post => (
                <div 
                  key={post.id} 
                  className={styles.postItem}
                  onClick={() => setSelectedPostId(post.id)}
                >
                  <div className={styles.postMain}>
                    <div className={styles.postAvatar}>{post.avatar}</div>
                    <div className={styles.postContent}>
                      <h3 className={styles.postTitle}>{post.title}</h3>
                      {post.preview && (
                        <p className={styles.postPreview}>{post.preview}</p>
                      )}
                      <div className={styles.postMeta}>
                        <span className={styles.postAuthor}>{post.author}</span>
                        <span className={styles.metaDot}>•</span>
                        <span className={styles.postDate}>
                          <Clock size={12} />
                          {post.date}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className={styles.postActions}>
                    <button 
                      className={styles.actionBtn}
                      onClick={(e) => {
                        e.stopPropagation();
                        // 更多操作
                      }}
                    >
                      <MoreVertical size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </main>

          {/* 右侧对话区 */}
          <aside className={styles.chatArea}>
            {selectedPost ? (
              <div className={styles.docPanel}>
                <div className={styles.docHeader}>
                  <button className={styles.docBackBtn} onClick={() => setSelectedPostId(null)}>
                    <ArrowLeft size={16} /> 返回
                  </button>
                  <h2 className={styles.docTitle}>{selectedPost.title}</h2>
                  <div className={styles.docMeta}>
                    <span>{selectedPost.author}</span>
                    <span className={styles.metaDot}>•</span>
                    <span>{selectedPost.date}</span>
                  </div>
                </div>
                <div className={styles.docBody}>
                  {(postContentById[selectedPost.id] || '暂无内容').split('\n').map((line, idx) => (
                    <p key={idx} className={styles.docP}>{line}</p>
                  ))}
                </div>
              </div>
            ) : (
              <>
                <div className={styles.chatHeader}>
                  <MessageCircle size={18} />
                  <span>提问本知识库</span>
                </div>
                <div className={styles.chatContent}>
                  <div className={styles.chatWelcome}>
                    <p className={styles.welcomeText}>Hi，你可以看看向本知识库：</p>
                    <div className={styles.suggestions}>
                      <button className={styles.suggestionItem} onClick={() => setAskInput('微星 GS65 现在的性价比多少？')}>微星 GS65 现在的性价比多少？</button>
                      <button className={styles.suggestionItem} onClick={() => setAskInput('白色外壳容易掉色吗？')}>白色外壳容易掉色吗？</button>
                      <button className={styles.suggestionItem} onClick={() => setAskInput('小米笔记本 Pro X15 的键盘手感如何？')}>小米笔记本 Pro X15的键盘手感如何？</button>
                    </div>
                  </div>
                </div>
                <div className={styles.chatInput}>
                  <div className={styles.quickActions}>
                    <button className={styles.quickBtn} onClick={() => setAskInput('请结合本知识库生成一段观点洞察：')}>
                      <Sparkles size={14} />
                      观点洞察
                    </button>
                    <button className={styles.quickBtn} onClick={() => setAskInput('请按时间给出关键事件脉络：')}>
                      <Clock size={14} />
                      时间脉络
                    </button>
                    <button className={styles.quickBtn} onClick={() => setAskInput('请为以下网页生成摘要：')}>
                      <Globe size={14} />
                      网页摘要
                    </button>
                  </div>
                  <div className={styles.inputWrap}>
                    <input 
                      className={styles.textInput}
                      placeholder="可对本知识库进行提问..."
                      value={askInput}
                      onChange={(e) => setAskInput(e.target.value)}
                    />
                    <button className={styles.sendBtn} onClick={() => { if (askInput.trim()) { console.log('Ask:', askInput); setAskInput(''); } }}>
                      <Send size={18} />
                    </button>
                  </div>
                  <div className={styles.disclaimer}>
                    结果由 AI 大模型生成，禁止上传涉密、违法内容，请谨慎使用。
                  </div>
                </div>
              </>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}


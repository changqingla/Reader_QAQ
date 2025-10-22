import React from 'react';
import Sidebar from '@/components/Sidebar/Sidebar';
import { 
  Search, 
  FileText, 
  Database, 
  Star,
  Grid3x3,
  List,
  MoreVertical
} from 'lucide-react';
import styles from './Favorites.module.css';

interface FavoriteItem {
  id: string;
  type: 'paper' | 'knowledge';
  title: string;
  description: string;
  author?: string;
  date: string;
  source?: string;
  tags?: string[];
}

// 模拟数据
const mockFavorites: FavoriteItem[] = [
  {
    id: '1',
    type: 'paper',
    title: 'Attention Is All You Need',
    description: 'Transformer模型的开创性论文，提出了完全基于注意力机制的神经网络架构...',
    author: 'Vaswani et al.',
    date: '2023-12-15',
    source: 'arXiv',
    tags: ['Deep Learning', 'NLP', 'Transformer']
  },
  {
    id: '2',
    type: 'knowledge',
    title: 'AI 技术前沿',
    description: '包含最新AI研究论文、技术博客和行业报告的综合知识库',
    date: '2024-01-10',
    tags: ['AI', '机器学习', '研究']
  },
  {
    id: '3',
    type: 'paper',
    title: 'BERT: Pre-training of Deep Bidirectional Transformers',
    description: 'BERT模型论文，革新了NLP领域的预训练方法...',
    author: 'Devlin et al.',
    date: '2023-12-20',
    source: 'Google Research',
    tags: ['NLP', 'Pre-training', 'BERT']
  },
  {
    id: '4',
    type: 'knowledge',
    title: '产品设计精选',
    description: '收集了优秀的产品设计案例、用户体验研究和设计理论',
    date: '2024-01-05',
    tags: ['设计', 'UX', '产品']
  },
  {
    id: '5',
    type: 'paper',
    title: 'GPT-4 Technical Report',
    description: 'OpenAI发布的GPT-4技术报告，详细介绍了模型架构和性能...',
    author: 'OpenAI',
    date: '2024-01-15',
    source: 'OpenAI',
    tags: ['LLM', 'GPT', 'AI']
  },
  {
    id: '6',
    type: 'knowledge',
    title: '前端开发资源库',
    description: '前端开发相关的教程、工具、框架文档和最佳实践',
    date: '2023-12-28',
    tags: ['前端', 'React', 'Web开发']
  }
];

export default function Favorites() {
  const [selectedChatId, setSelectedChatId] = React.useState<string | undefined>();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [filterType, setFilterType] = React.useState<'all' | 'paper' | 'knowledge'>('all');
  const [viewMode, setViewMode] = React.useState<'grid' | 'list'>('list');

  React.useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  const filteredFavorites = React.useMemo(() => {
    let result = mockFavorites;
    
    if (filterType !== 'all') {
      result = result.filter(item => item.type === filterType);
    }
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(item => 
        item.title.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query) ||
        item.tags?.some(tag => tag.toLowerCase().includes(query))
      );
    }
    
    return result;
  }, [filterType, searchQuery]);

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

      {/* Main Content */}
      <div className={styles.main}>
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <Star className={styles.headerIcon} size={24} />
            <h1 className={styles.title}>我的收藏</h1>
          </div>
          <div className={styles.headerStats}>
            <span className={styles.statItem}>
              {filteredFavorites.length} 项收藏
            </span>
          </div>
        </div>

        <div className={styles.content}>
          {/* Toolbar */}
          <div className={styles.toolbar}>
            <div className={styles.searchWrap}>
              <Search className={styles.searchIcon} size={18} />
              <input
                type="text"
                className={styles.searchInput}
                placeholder="搜索收藏的内容..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className={styles.toolbarRight}>
              <div className={styles.filterGroup}>
                <button
                  className={`${styles.filterBtn} ${filterType === 'all' ? styles.filterActive : ''}`}
                  onClick={() => setFilterType('all')}
                >
                  全部
                </button>
                <button
                  className={`${styles.filterBtn} ${filterType === 'paper' ? styles.filterActive : ''}`}
                  onClick={() => setFilterType('paper')}
                >
                  <FileText size={14} />
                  论文
                </button>
                <button
                  className={`${styles.filterBtn} ${filterType === 'knowledge' ? styles.filterActive : ''}`}
                  onClick={() => setFilterType('knowledge')}
                >
                  <Database size={14} />
                  知识库
                </button>
              </div>

              <div className={styles.viewToggle}>
                <button
                  className={`${styles.viewBtn} ${viewMode === 'grid' ? styles.viewActive : ''}`}
                  onClick={() => setViewMode('grid')}
                  title="网格视图"
                >
                  <Grid3x3 size={16} />
                </button>
                <button
                  className={`${styles.viewBtn} ${viewMode === 'list' ? styles.viewActive : ''}`}
                  onClick={() => setViewMode('list')}
                  title="列表视图"
                >
                  <List size={16} />
                </button>
              </div>
            </div>
          </div>

          {/* Content Area */}
          {filteredFavorites.length === 0 ? (
            <div className={styles.emptyState}>
              <Star className={styles.emptyIcon} size={48} />
              <p className={styles.emptyText}>
                {searchQuery ? '没有找到匹配的收藏' : '还没有收藏任何内容'}
              </p>
            </div>
          ) : (
            <div className={styles.favoritesList}>
              {filteredFavorites.map((item) => (
                <div key={item.id} className={styles.favoriteItem}>
                  <div className={styles.itemLeft}>
                    <div className={styles.itemIcon}>
                      {item.type === 'paper' ? (
                        <FileText size={18} />
                      ) : (
                        <Database size={18} />
                      )}
                    </div>
                    <div className={styles.itemContent}>
                      <h3 className={styles.itemTitle}>{item.title}</h3>
                      <p className={styles.itemDesc}>{item.description}</p>
                      <div className={styles.itemMeta}>
                        {item.author && <span>{item.author}</span>}
                        {item.author && <span className={styles.metaDot}>•</span>}
                        <span>{item.date}</span>
                        {item.source && (
                          <>
                            <span className={styles.metaDot}>•</span>
                            <span>{item.source}</span>
                          </>
                        )}
                      </div>
                      {item.tags && item.tags.length > 0 && (
                        <div className={styles.itemTags}>
                          {item.tags.map((tag, idx) => (
                            <span key={idx} className={styles.tagChip}>{tag}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className={styles.itemActions}>
                    <button className={styles.starBtn} title="取消收藏">
                      <Star size={16} />
                    </button>
                    <button className={styles.moreBtn} title="更多">
                      <MoreVertical size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

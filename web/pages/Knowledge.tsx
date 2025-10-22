import React, { useMemo, useState } from 'react';
import { Search, Plus, Folder, Database, Rss, ChevronDown, Users } from 'lucide-react';
import Sidebar from '@/components/Sidebar/Sidebar';
import CreateKnowledgeModal from '@/components/CreateKnowledgeModal/CreateKnowledgeModal';
import { useNavigate } from 'react-router-dom';
import styles from './Knowledge.module.css';

interface HubItem {
  id: string;
  title: string;
  desc: string;
  icon: string;
  subs: number; // 订阅
  contents: number; // 内容数
}

const mockHub: HubItem[] = Array.from({ length: 20 }).map((_, i) => ({
  id: String(i + 1),
  title: ['DeepSeek 知识库','AI 智能体','金庸武侠','心理学与生活','R 机器学习','辩之论之','宇宙万象','诺奖书友圈'][i % 8] + ` · ${i+1}`,
  desc: '这里面包含了各种热门的知识、材料与话题，欢迎一起分享与订阅。',
  icon: '📘',
  subs: 170 + i * 3,
  contents: 40 + (i % 9) * 2,
}));

export default function Knowledge() {
  const navigate = useNavigate();
  const [selectedChatId, setSelectedChatId] = useState<string | undefined>();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [query, setQuery] = useState('');
  const [activeTag, setActiveTag] = useState('推荐');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [myKnowledgeBases, setMyKnowledgeBases] = useState([
    { id: 'default', name: '默认知识库', description: '', tags: [] }
  ]);

  React.useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return mockHub;
    return mockHub.filter(i => i.title.toLowerCase().includes(q) || i.desc.toLowerCase().includes(q));
  }, [query]);

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

      {/* 左侧主侧边栏 */}
      <div className={`${styles.sidebarContainer} ${isMobile && isSidebarOpen ? styles.open : ''}`}>
        <Sidebar onNewChat={() => setSelectedChatId(undefined)} onSelectChat={(id) => setSelectedChatId(id)} selectedChatId={selectedChatId} />
      </div>

      {/* 新建知识库弹窗 */}
      <CreateKnowledgeModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleAddKnowledgeBase}
      />

      {/* 右侧内容区域：二级侧栏 + 主区 */}
      <div className={styles.main}>
        <div className={styles.hubHeader}>知识广场</div>

        <div className={styles.contentArea}>
          {/* 二级侧栏 */}
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
              {myKnowledgeBases.map(kb => (
                <button
                  key={kb.id}
                  className={styles.myItem}
                  onClick={() => navigate(kb.id === 'default' ? '/knowledge/default' : `/knowledge/${kb.id}`)}
                  aria-label={`打开${kb.name}`}
                >
                  <span className={styles.myDot} />
                  {kb.name}
                </button>
              ))}
            </div>

            <div className={styles.sectionCollapse}>
              <button className={styles.collapseBtnSm}><ChevronDown size={14} /> 订阅</button>
              <div className={styles.subscribeList}>
                <div className={styles.subItem}><Folder size={14} /> 知识库</div>
                <div className={styles.subItem}><Rss size={14} /> RSS</div>
              </div>
            </div>
          </aside>

          {/* 主内容区 */}
          <section className={styles.hubMain}>
            <div className={styles.searchWrap}>
              <Search size={18} className={styles.searchIcon} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className={styles.search}
                placeholder="试试搜索感兴趣的知识库"
              />
            </div>

            <div className={styles.tags}>
              {['推荐','2025 年度精选','科学技术','学习','热门社区'].map(t => (
                <button
                  key={t}
                  className={`${styles.tag} ${activeTag === t ? styles.tagActive : ''}`}
                  onClick={() => setActiveTag(t)}
                >{t}</button>
              ))}
            </div>

            <div className={styles.feed}>
              {filtered.map(item => (
                <div 
                  key={item.id} 
                  className={styles.feedItem}
                  onClick={() => navigate(`/knowledge/hub/${item.id}`)}
                  role="button"
                  tabIndex={0}
                >
                  <div className={styles.feedIcon}>{item.icon}</div>
                  <div className={styles.feedBody}>
                    <div className={styles.feedTitle}>{item.title}</div>
                    <div className={styles.feedDesc}>{item.desc}</div>
                    <div className={styles.feedMeta}>
                      <span className={styles.metaChip}><Users size={14} /> {item.subs} 订阅</span>
                      <span className={styles.metaChip}><Database size={14} /> {item.contents} 内容</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}



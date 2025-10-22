import React from 'react';
import Sidebar from '@/components/Sidebar/Sidebar';
import { 
  Search, 
  Plus, 
  ChevronDown, 
  Folder,
  Rss,
  ArrowLeft,
  Clock,
  User,
  Tag
} from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import styles from './PostDetail.module.css';

export default function PostDetail() {
  const navigate = useNavigate();
  const { hubId, postId } = useParams();
  const [selectedChatId, setSelectedChatId] = React.useState<string | undefined>();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);

  React.useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  // 模拟文档数据
  const postData = {
    title: '笔记本科普与选购',
    author: '鹿鹿',
    date: '2024-10-20',
    tags: ['笔记本', '选购指南', '科普'],
    content: `# 笔记本电脑选购指南

## 一、确定使用场景

在选购笔记本之前，首先要明确自己的使用需求：

### 1. 办公轻薄本
适合日常办公、文档处理、网页浏览等轻度使用场景。
- **特点**：轻薄便携、续航时间长
- **推荐配置**：i5/R5处理器 + 16GB内存 + 集成显卡
- **价格区间**：3000-6000元

### 2. 全能本
适合轻度游戏、视频剪辑、编程开发等中度使用。
- **特点**：性能均衡、便携性尚可
- **推荐配置**：i7/R7处理器 + 16GB内存 + MX系列独显
- **价格区间**：5000-8000元

### 3. 游戏本
适合3A游戏、专业设计、深度学习等重度使用。
- **特点**：性能强劲、散热优秀
- **推荐配置**：i7/R7处理器 + 32GB内存 + RTX系列独显
- **价格区间**：7000-15000元

## 二、关键配置解析

### CPU（处理器）
- **Intel**：i5适合日常使用，i7适合专业工作
- **AMD**：R5性价比高，R7性能强劲
- 建议选择12代Intel或6000系AMD以上

### 内存
- **8GB**：仅够基本使用
- **16GB**：当前主流配置（推荐）
- **32GB**：专业需求或重度多任务

### 硬盘
- **建议512GB起步**，日常使用够用
- **1TB**：存储大量文件、游戏
- 优先选择PCIe 4.0 NVMe固态硬盘

### 显卡
- **集显**：Intel Iris Xe / AMD Radeon
- **入门独显**：MX550/MX570
- **游戏独显**：RTX 4050/4060/4070

## 三、屏幕选择

### 分辨率
- **1920×1080**（FHD）：主流配置
- **2560×1600**（2.5K）：更清晰细腻
- **3840×2160**（4K）：专业设计需求

### 刷新率
- **60Hz**：日常使用
- **120Hz/144Hz**：游戏、视频剪辑
- **165Hz及以上**：电竞需求

### 色域
- **45% NTSC**：基本够用
- **72% NTSC（100% sRGB）**：推荐标准
- **100% Adobe RGB / P3**：专业设计

## 四、品牌推荐

### 轻薄本
1. **联想小新**：性价比之王
2. **华为MateBook**：做工精良
3. **Dell XPS**：高端之选
4. **MacBook Air**：苹果生态

### 游戏本
1. **联想拯救者**：散热优秀
2. **华硕天选**：性价比高
3. **惠普暗影精灵**：外观时尚
4. **外星人/ROG**：高端选择

## 五、购买建议

1. **618、双11等大促期间**价格更优惠
2. **线上购买**更便宜，线下可以体验后网购
3. 注意区分**同名不同配置**的版本
4. 关注**售后服务**，建议购买延保
5. 查看**真实用户评价**，避免刷单好评

## 六、常见误区

❌ **CPU代数越高越好** - 同代低配比上代高配更值
❌ **内存越大越好** - 根据需求选择，避免浪费
❌ **显卡显存越大越好** - 核心性能更重要
❌ **品牌决定一切** - 配置和价格才是关键

---

希望这份指南能帮助你选到合适的笔记本！`
  };

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
            <button className={styles.backBtn} onClick={() => navigate(`/knowledge/hub/${hubId}`)}>
              <ArrowLeft size={16} />
              <span>返回</span>
            </button>

            <div className={styles.subSearch}>
              <Search size={16} className={styles.subSearchIcon} />
              <input 
                className={styles.subSearchInput} 
                placeholder="搜索你的知识库"
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

          {/* 中间文档内容区 */}
          <main className={styles.documentContent}>
            <article className={styles.article}>
              <header className={styles.articleHeader}>
                <h1 className={styles.articleTitle}>{postData.title}</h1>
                <div className={styles.articleMeta}>
                  <span className={styles.metaItem}>
                    <User size={14} />
                    {postData.author}
                  </span>
                  <span className={styles.metaDot}>•</span>
                  <span className={styles.metaItem}>
                    <Clock size={14} />
                    {postData.date}
                  </span>
                </div>
                {postData.tags && postData.tags.length > 0 && (
                  <div className={styles.articleTags}>
                    <Tag size={14} />
                    {postData.tags.map((tag, idx) => (
                      <span key={idx} className={styles.tagItem}>{tag}</span>
                    ))}
                  </div>
                )}
              </header>

              <div className={styles.articleBody}>
                {postData.content.split('\n').map((line, idx) => {
                  if (line.startsWith('# ')) {
                    return <h1 key={idx} className={styles.h1}>{line.slice(2)}</h1>;
                  } else if (line.startsWith('## ')) {
                    return <h2 key={idx} className={styles.h2}>{line.slice(3)}</h2>;
                  } else if (line.startsWith('### ')) {
                    return <h3 key={idx} className={styles.h3}>{line.slice(4)}</h3>;
                  } else if (line.startsWith('- ')) {
                    return <li key={idx} className={styles.li}>{line.slice(2)}</li>;
                  } else if (line.startsWith('---')) {
                    return <hr key={idx} className={styles.hr} />;
                  } else if (line.startsWith('❌')) {
                    return <p key={idx} className={styles.warning}>{line}</p>;
                  } else if (line.trim() === '') {
                    return <div key={idx} className={styles.spacer} />;
                  } else {
                    return <p key={idx} className={styles.p}>{line}</p>;
                  }
                })}
              </div>
            </article>
          </main>
        </div>
      </div>
    </div>
  );
}


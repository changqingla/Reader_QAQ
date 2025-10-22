import React from 'react';
import Sidebar from '@/components/Sidebar/Sidebar';
import { 
  Search, 
  Plus,
  Folder,
  Tag,
  Trash2,
  MoreVertical,
  Edit3,
  Clock,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import styles from './Notes.module.css';

interface Note {
  id: string;
  title: string;
  content: string;
  folder: string;
  tags: string[];
  updatedAt: string;
  createdAt: string;
}

// 模拟笔记数据
const mockNotes: Note[] = [
  {
    id: '1',
    title: '产品需求整理',
    content: '1. 用户登录注册功能\n2. 个人资料页面\n3. 消息通知系统\n4. 搜索功能优化\n\n需要与设计团队确认UI细节，预计下周三前完成原型图。',
    folder: '工作',
    tags: ['产品', '需求'],
    updatedAt: '2024-01-20 14:30',
    createdAt: '2024-01-18 09:15'
  },
  {
    id: '2',
    title: '读书笔记 - 《人类简史》',
    content: '第三章：人类的融合统一\n\n• 智人通过虚构故事建立大规模协作\n• 农业革命改变了人类社会结构\n• 文字的出现推动了文明发展\n\n思考：现代社会的协作机制与古代有何不同？',
    folder: '个人',
    tags: ['读书', '历史'],
    updatedAt: '2024-01-19 21:45',
    createdAt: '2024-01-15 10:20'
  },
  {
    id: '3',
    title: '周末计划',
    content: '周六：\n- 早上去健身房\n- 下午整理房间\n- 晚上和朋友聚餐\n\n周日：\n- 学习React新特性\n- 写技术博客\n- 准备下周工作',
    folder: '生活',
    tags: ['计划'],
    updatedAt: '2024-01-19 08:15',
    createdAt: '2024-01-19 08:15'
  },
  {
    id: '4',
    title: '会议记录 - 项目评审',
    content: '时间：2024-01-18 15:00\n参会人：张三、李四、王五\n\n讨论要点：\n1. 项目进度汇报\n2. 技术难点分析\n3. 下一步计划\n\nAction Items：\n- 张三：完成数据库设计\n- 李四：搭建开发环境',
    folder: '工作',
    tags: ['会议', '项目'],
    updatedAt: '2024-01-18 16:30',
    createdAt: '2024-01-18 15:00'
  },
  {
    id: '5',
    title: '技术学习清单',
    content: 'Q1学习目标：\n\n前端：\n□ React 18新特性\n□ TypeScript进阶\n□ 性能优化技巧\n\n后端：\n□ Node.js最佳实践\n□ 数据库优化\n□ 微服务架构',
    folder: '工作',
    tags: ['学习', '技术'],
    updatedAt: '2024-01-17 22:00',
    createdAt: '2024-01-10 09:00'
  }
];

const folders = ['全部', '工作', '个人', '生活'];

export default function Notes() {
  const [selectedChatId, setSelectedChatId] = React.useState<string | undefined>();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedFolder, setSelectedFolder] = React.useState('全部');
  const [selectedNote, setSelectedNote] = React.useState<Note | null>(mockNotes[0]);
  const [noteContent, setNoteContent] = React.useState(mockNotes[0].content);
  const [noteTitle, setNoteTitle] = React.useState(mockNotes[0].title);

  React.useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  const filteredNotes = React.useMemo(() => {
    let result = mockNotes;
    
    if (selectedFolder !== '全部') {
      result = result.filter(note => note.folder === selectedFolder);
    }
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(note => 
        note.title.toLowerCase().includes(query) ||
        note.content.toLowerCase().includes(query) ||
        note.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }
    
    return result.sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  }, [selectedFolder, searchQuery]);

  const handleNoteClick = (note: Note) => {
    setSelectedNote(note);
    setNoteTitle(note.title);
    setNoteContent(note.content);
  };

  const handleNewNote = () => {
    const newNote: Note = {
      id: Date.now().toString(),
      title: '新笔记',
      content: '',
      folder: selectedFolder === '全部' ? '个人' : selectedFolder,
      tags: [],
      updatedAt: new Date().toLocaleString('zh-CN'),
      createdAt: new Date().toLocaleString('zh-CN')
    };
    setSelectedNote(newNote);
    setNoteTitle(newNote.title);
    setNoteContent(newNote.content);
  };

  // 粗粒度“润色”实现：
  // - 统一列表符号；
  // - 去除多余空行；
  // - 去除行首尾空白；
  const polishContent = (content: string) => {
    const normalizedBullets = content
      .replace(/^[\-•]\s?/gm, '• ')
      .replace(/\t/g, '  ');
    const trimmedLines = normalizedBullets
      .split('\n')
      .map(l => l.trimEnd())
      .join('\n');
    // 合并3个以上的空行为1个
    return trimmedLines.replace(/\n{3,}/g, '\n\n');
  };

  const handlePolish = () => {
    setNoteContent(polishContent(noteContent));
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

      {/* Notes Layout */}
      <div className={styles.notesContainer}>
        {/* Folders Sidebar */}
        <div className={styles.folderSidebar}>
          <div className={styles.folderHeader}>
            <h2 className={styles.folderTitle}>文件夹</h2>
            <button className={styles.iconBtn} title="新建文件夹">
              <Plus size={16} />
            </button>
          </div>

          <div className={styles.folderList}>
            {folders.map(folder => (
              <button
                key={folder}
                className={`${styles.folderItem} ${selectedFolder === folder ? styles.folderActive : ''}`}
                onClick={() => setSelectedFolder(folder)}
              >
                <Folder size={16} />
                <span>{folder}</span>
                <span className={styles.folderCount}>
                  {folder === '全部' 
                    ? mockNotes.length 
                    : mockNotes.filter(n => n.folder === folder).length
                  }
                </span>
              </button>
            ))}
          </div>

          <div className={styles.folderSection}>
            <div className={styles.sectionTitle}>
              <Tag size={14} />
              <span>标签</span>
            </div>
            <div className={styles.tagList}>
              {['产品', '技术', '读书', '会议', '计划'].map(tag => (
                <button key={tag} className={styles.tagItem}>
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Notes List */}
        <div className={styles.notesList}>
          <div className={styles.notesHeader}>
            <div className={styles.searchWrap}>
              <Search className={styles.searchIcon} size={16} />
              <input
                type="text"
                className={styles.searchInput}
                placeholder="搜索笔记..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button className={styles.newNoteBtn} onClick={handleNewNote}>
              <Plus size={18} />
              新笔记
            </button>
          </div>

          <div className={styles.notesScroll}>
            {filteredNotes.length === 0 ? (
              <div className={styles.emptyNotes}>
                <Edit3 size={40} className={styles.emptyIcon} />
                <p>没有找到笔记</p>
              </div>
            ) : (
              filteredNotes.map(note => (
                <div
                  key={note.id}
                  className={`${styles.noteItem} ${selectedNote?.id === note.id ? styles.noteActive : ''}`}
                  onClick={() => handleNoteClick(note)}
                >
                  <div className={styles.noteItemHeader}>
                    <h3 className={styles.noteItemTitle}>{note.title}</h3>
                    <button className={styles.noteMenuBtn}>
                      <MoreVertical size={14} />
                    </button>
                  </div>
                  <p className={styles.noteItemPreview}>
                    {note.content.slice(0, 80)}...
                  </p>
                  <div className={styles.noteItemMeta}>
                    <span className={styles.noteTime}>
                      <Clock size={12} />
                      {note.updatedAt.split(' ')[0]}
                    </span>
                    {note.tags.length > 0 && (
                      <div className={styles.noteTags}>
                        {note.tags.slice(0, 2).map((tag, idx) => (
                          <span key={idx} className={styles.noteTag}>{tag}</span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Note Editor */}
        <div className={styles.noteEditor}>
          {selectedNote ? (
            <>
              <div className={styles.editorHeader}>
                <input
                  type="text"
                  className={styles.titleInput}
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  placeholder="笔记标题"
                />
                <div className={styles.editorActions}>
                  <button className={styles.aiBtn} onClick={handlePolish} title="AI润色">
                    <Sparkles size={16} />
                    <span>AI润色</span>
                  </button>
                  <button className={styles.editorBtn}>
                    <Tag size={16} />
                  </button>
                  <button className={styles.editorBtn}>
                    <Trash2 size={16} />
                  </button>
                  <button className={styles.editorBtn}>
                    <MoreVertical size={16} />
                  </button>
                </div>
              </div>

              <div className={styles.editorMeta}>
                <span className={styles.metaItem}>
                  <Folder size={14} />
                  {selectedNote.folder}
                </span>
                <ChevronRight size={12} className={styles.metaSeparator} />
                <span className={styles.metaItem}>
                  最后编辑 {selectedNote.updatedAt}
                </span>
              </div>

              <textarea
                className={styles.contentArea}
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                placeholder="开始写笔记..."
              />
            </>
          ) : (
            <div className={styles.editorEmpty}>
              <Edit3 size={48} className={styles.emptyIcon} />
              <p>选择一条笔记或创建新笔记</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

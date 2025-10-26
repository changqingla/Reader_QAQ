/**
 * 笔记页面
 * 完整实现文件夹管理、笔记CRUD、自动保存
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '@/components/Sidebar/Sidebar';
import { api, noteAPI } from '@/lib/api';
import { useToast } from '@/hooks/useToast';
import { useChatSessions } from '@/hooks/useChatSessions';
import ConfirmModal from '@/components/ConfirmModal/ConfirmModal';
import { 
  Search, 
  Plus,
  Folder,
  Trash2,
  MoreVertical,
  Edit3,
  Sparkles,
  X,
  Check
} from 'lucide-react';
import styles from './Notes.module.css';

interface Note {
  id: string;
  title: string;
  content: string;
  folderId?: string;
  tags: string[];
  updatedAt: string;
  createdAt: string;
}

interface FolderData {
  id: string;
  name: string;
  count: number;
}

const SYSTEM_FOLDERS = ['学习', '工作', '生活'];
const PROTECTED_FOLDER = '生活';

export default function Notes() {
  const toast = useToast();
  const navigate = useNavigate();
  const { chatSessions, refreshSessions } = useChatSessions();
  
  // UI State
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  
  // Data State
  const [folders, setFolders] = useState<FolderData[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string>('all');
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  
  // Search State
  const [searchQuery, setSearchQuery] = useState('');
  
  // Editor State
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [saving, setSaving] = useState(false);
  
  // Folder Edit State
  const [editingFolderId, setEditingFolderId] = useState<string | null>(null);
  const [editingFolderName, setEditingFolderName] = useState('');
  const [creatingFolder, setCreatingFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  
  // Modal State
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [folderToDelete, setFolderToDelete] = useState<FolderData | null>(null);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth <= 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  useEffect(() => {
    loadFolders();
  }, []);

  useEffect(() => {
    loadNotes();
  }, [selectedFolder, searchQuery]);

  // 自动保存
  useEffect(() => {
    if (!selectedNote) return;
    
    const hasChanges = noteTitle !== selectedNote.title || noteContent !== selectedNote.content;
    if (!hasChanges) return;

    setSaving(true);
    const timer = setTimeout(async () => {
      try {
        const response = await noteAPI.updateNote(selectedNote.id, {
          title: noteTitle,
          content: noteContent
        });
        
        const updatedAt = response?.updatedAt || new Date().toISOString();
        
        // 更新本地状态
        setNotes(prevNotes => prevNotes.map(n => 
          n.id === selectedNote.id 
            ? { ...n, title: noteTitle, content: noteContent, updatedAt }
            : n
        ));
        
        setSelectedNote(prev => prev ? { ...prev, title: noteTitle, content: noteContent, updatedAt } : null);
      } catch (error: any) {
        toast.error(error.message || '保存失败');
      } finally {
        setSaving(false);
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [noteTitle, noteContent, selectedNote, toast]);

  const loadFolders = async () => {
    try {
      const response = await noteAPI.listFolders();
      setFolders(response);
    } catch (error: any) {
      console.error('Failed to load folders:', error);
      toast.error(error.message || '加载文件夹失败');
    }
  };

  const loadNotes = async () => {
    try {
      const folderId = selectedFolder === 'all' ? undefined : selectedFolder;
      const response = await noteAPI.listNotes(folderId, searchQuery || undefined, 1, 100);
      setNotes(response.items);
    } catch (error: any) {
      console.error('Failed to load notes:', error);
      toast.error(error.message || '加载笔记失败');
    }
  };

  // 同步当前笔记状态到列表
  const syncCurrentNoteToList = useCallback(() => {
    if (selectedNote && (noteTitle !== selectedNote.title || noteContent !== selectedNote.content)) {
      setNotes(prevNotes => prevNotes.map(n => 
        n.id === selectedNote.id 
          ? { ...n, title: noteTitle, content: noteContent, updatedAt: new Date().toISOString() }
          : n
      ));
    }
  }, [selectedNote, noteTitle, noteContent]);

  const handleNoteClick = (note: Note) => {
    // 切换前同步当前笔记状态
    syncCurrentNoteToList();
    
    setSelectedNote(note);
    setNoteTitle(note.title);
    setNoteContent(note.content);
  };

  const handleNewNote = async () => {
    try {
      // 切换前同步当前笔记状态
      syncCurrentNoteToList();
      
      const folderId = selectedFolder === 'all' ? undefined : selectedFolder;
      const response = await noteAPI.createNote({
        title: '新笔记',
        content: '',
        folder: folderId,
        tags: []
      });
      
      await loadNotes();
      await loadFolders();
      
      // 创建完整的 Note 对象
      const newNote: Note = {
        id: response.id,
        title: response.title,
        content: response.content || '',
        folderId: response.folderId,
        tags: response.tags || [],
        updatedAt: response.updatedAt || new Date().toISOString(),
        createdAt: response.createdAt || new Date().toISOString()
      };
      
      setSelectedNote(newNote);
      setNoteTitle(newNote.title);
      setNoteContent(newNote.content);
      
      toast.success('笔记创建成功');
    } catch (error: any) {
      toast.error(error.message || '创建笔记失败');
    }
  };

  const handleDeleteNote = async () => {
    if (!selectedNote) return;
    
    try {
      await noteAPI.deleteNote(selectedNote.id);
      await loadNotes();
      await loadFolders();
      
      setSelectedNote(null);
      setNoteTitle('');
      setNoteContent('');
      
      toast.success('笔记已删除');
    } catch (error: any) {
      toast.error(error.message || '删除笔记失败');
    }
  };

  // 文件夹管理
  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) {
      toast.warning('请输入文件夹名称');
      return;
    }

    if (SYSTEM_FOLDERS.includes(newFolderName.trim())) {
      toast.warning('不能使用系统默认文件夹名称');
      return;
    }

    try {
      await noteAPI.createFolder(newFolderName.trim());
      await loadFolders();
      setCreatingFolder(false);
      setNewFolderName('');
      toast.success('文件夹创建成功');
    } catch (error: any) {
      toast.error(error.message || '创建文件夹失败');
    }
  };

  const handleRenameFolder = async (folder: FolderData) => {
    if (folder.name === PROTECTED_FOLDER) {
      toast.warning('生活才是生命的真谛，不允许重命名');
      return;
    }
    
    setEditingFolderId(folder.id);
    setEditingFolderName(folder.name);
    setOpenMenuId(null);
  };

  const handleSaveRename = async () => {
    if (!editingFolderId) return;
    
    if (!editingFolderName.trim()) {
      toast.warning('文件夹名称不能为空');
      return;
    }

    if (SYSTEM_FOLDERS.includes(editingFolderName.trim())) {
      toast.warning('不能使用系统默认文件夹名称');
      return;
    }

    try {
      await noteAPI.renameFolder(editingFolderId, editingFolderName.trim());
      await loadFolders();
      setEditingFolderId(null);
      setEditingFolderName('');
      toast.success('文件夹重命名成功');
    } catch (error: any) {
      toast.error(error.message || '重命名失败');
    }
  };

  const handleDeleteFolder = (folder: FolderData) => {
    if (folder.name === PROTECTED_FOLDER) {
      toast.warning('生活才是生命的真谛，不允许删除');
      return;
    }
    
    setFolderToDelete(folder);
    setDeleteModalOpen(true);
    setOpenMenuId(null);
  };

  const confirmDeleteFolder = async () => {
    if (!folderToDelete) return;
    
    try {
      await noteAPI.deleteFolder(folderToDelete.id);
      await loadFolders();
      await loadNotes();
      
      if (selectedFolder === folderToDelete.id) {
        setSelectedFolder('all');
      }
      
      toast.success('文件夹已删除');
    } catch (error: any) {
      toast.error(error.message || '删除文件夹失败');
    } finally {
      setDeleteModalOpen(false);
      setFolderToDelete(null);
    }
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

      <ConfirmModal
        isOpen={deleteModalOpen}
        title="删除文件夹"
        message={`确定要删除文件夹「${folderToDelete?.name}」吗？文件夹中的笔记将移至「全部」。`}
        type="danger"
        confirmText="删除"
        cancelText="取消"
        onConfirm={confirmDeleteFolder}
        onCancel={() => {
          setDeleteModalOpen(false);
          setFolderToDelete(null);
        }}
      />

      <div className={styles.main}>
        <div className={styles.contentArea}>
          {/* 左侧：文件夹列表 */}
          <aside className={styles.folderSidebar}>
            <div className={styles.sidebarHeader}>
              <h2 className={styles.sidebarTitle}>我的笔记</h2>
              <button 
                className={styles.addFolderBtn}
                onClick={() => setCreatingFolder(true)}
                title="新建文件夹"
              >
                <Plus size={16} />
              </button>
            </div>

            <div className={styles.folderList}>
              <button
                className={`${styles.folderItem} ${selectedFolder === 'all' ? styles.folderActive : ''}`}
                onClick={() => setSelectedFolder('all')}
              >
                <Folder size={16} />
                <span>全部</span>
                <span className={styles.folderCount}>
                  {folders.reduce((sum, f) => sum + f.count, 0)}
                </span>
              </button>

              {folders.map(folder => (
                <div key={folder.id} className={styles.folderItemWrapper}>
                  {editingFolderId === folder.id ? (
                    <div className={styles.folderEdit}>
                      <input
                        type="text"
                        value={editingFolderName}
                        onChange={(e) => setEditingFolderName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveRename();
                          if (e.key === 'Escape') setEditingFolderId(null);
                        }}
                        onBlur={handleSaveRename}
                        className={styles.folderInput}
                        autoFocus
                      />
                      <button onClick={handleSaveRename} className={styles.saveBtn}>
                        <Check size={14} />
                      </button>
                    </div>
                  ) : (
                    <>
                      <button
                        className={`${styles.folderItem} ${selectedFolder === folder.id ? styles.folderActive : ''}`}
                        onClick={() => setSelectedFolder(folder.id)}
                      >
                        <Folder size={16} />
                        <span>{folder.name}</span>
                        <span className={styles.folderCount}>{folder.count}</span>
                      </button>
                      <div className={styles.folderMenu}>
                        <button
                          className={styles.menuBtn}
                          onClick={() => setOpenMenuId(openMenuId === folder.id ? null : folder.id)}
                        >
                          <MoreVertical size={14} />
                        </button>
                        {openMenuId === folder.id && (
                          <div className={styles.menuDropdown}>
                            <button
                              className={styles.menuItem}
                              onClick={() => handleRenameFolder(folder)}
                            >
                              <Edit3 size={14} />
                              重命名
                            </button>
                            <button
                              className={`${styles.menuItem} ${styles.menuItemDanger}`}
                              onClick={() => handleDeleteFolder(folder)}
                            >
                              <Trash2 size={14} />
                              删除
                            </button>
                          </div>
                        )}
                      </div>
                    </>
                  )}
                </div>
              ))}

              {creatingFolder && (
                <div className={styles.folderEdit}>
                  <input
                    type="text"
                    value={newFolderName}
                    onChange={(e) => setNewFolderName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleCreateFolder();
                      if (e.key === 'Escape') {
                        setCreatingFolder(false);
                        setNewFolderName('');
                      }
                    }}
                    onBlur={() => {
                      if (newFolderName.trim()) {
                        handleCreateFolder();
                      } else {
                        setCreatingFolder(false);
                      }
                    }}
                    className={styles.folderInput}
                    placeholder="未命名的文件夹"
                    autoFocus
                  />
                  <button onClick={handleCreateFolder} className={styles.saveBtn}>
                    <Check size={14} />
                  </button>
                </div>
              )}
            </div>
          </aside>

          {/* 中间：笔记列表 */}
          <section className={styles.notesList}>
            <div className={styles.notesHeader}>
              <div className={styles.searchWrap}>
                <Search size={16} />
                <input
                  type="text"
                  placeholder="搜索笔记..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={styles.searchInput}
                />
              </div>
              <button className={styles.newNoteBtn} onClick={handleNewNote}>
                <Plus size={16} />
                新笔记
              </button>
            </div>

            <div className={styles.notesContent}>
              {notes.length === 0 ? (
                <div className={styles.emptyNotes}>
                  <Edit3 size={48} className={styles.emptyIcon} />
                  <p>{searchQuery ? '没有找到笔记' : '还没有笔记，点击"新笔记"开始'}</p>
                </div>
              ) : (
                notes.map(note => (
                  <div
                    key={note.id}
                    className={`${styles.noteItem} ${selectedNote?.id === note.id ? styles.noteActive : ''}`}
                    onClick={() => handleNoteClick(note)}
                  >
                    <div className={styles.noteTitle}>{note.title || '无标题'}</div>
                    <div className={styles.notePreview}>
                      {note.content.substring(0, 100) || '空笔记'}
                    </div>
                    <div className={styles.noteMeta}>
                      {new Date(note.updatedAt).toLocaleString('zh-CN', {
                        month: 'numeric',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>

          {/* 右侧：编辑器 */}
          <section className={styles.editor}>
            {selectedNote ? (
              <>
                <div className={styles.editorHeader}>
                  <input
                    type="text"
                    value={noteTitle}
                    onChange={(e) => setNoteTitle(e.target.value)}
                    className={styles.editorTitle}
                    placeholder="笔记标题"
                  />
                  <div className={styles.editorActions}>
                    {saving && <span className={styles.savingText}>保存中...</span>}
                    {!saving && selectedNote && (
                      <span className={styles.savedText}>
                        {new Date(selectedNote.updatedAt).toLocaleString('zh-CN', {
                          month: 'numeric',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    )}
                    <button
                      className={styles.polishBtn}
                      title="AI润色（暂未实现）"
                      disabled
                    >
                      <Sparkles size={16} />
                    </button>
                    <button
                      className={styles.deleteBtn}
                      onClick={handleDeleteNote}
                      title="删除笔记"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
                <textarea
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  className={styles.editorContent}
                  placeholder="开始写笔记..."
                />
              </>
            ) : (
              <div className={styles.editorEmpty}>
                <Edit3 size={64} className={styles.emptyIcon} />
                <p>选择一个笔记开始编辑</p>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}

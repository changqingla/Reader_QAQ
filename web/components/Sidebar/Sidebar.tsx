import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Sun, Moon, Headphones, LogOut, Book, Star, Notebook, ChevronsLeft, ChevronsRight } from 'lucide-react';
import styles from './Sidebar.module.css';
import { useTheme } from '@/hooks/useTheme';

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
}

const mockChats: Chat[] = [
  {
    id: '1',
    title: 'Typo Assistance Request',
    lastMessage: 'Help me fix typos in my document',
    timestamp: '2 hours ago'
  },
  {
    id: '2', 
    title: 'Quadratic Function Plot',
    lastMessage: 'How to plot quadratic functions?',
    timestamp: '1 day ago'
  },
  {
    id: '3',
    title: 'Toyota Names Poetry',
    lastMessage: 'Write a poem about Toyota car names',
    timestamp: '2 days ago'
  }
];

interface SidebarProps {
  onNewChat: () => void;
  onSelectChat: (chatId: string) => void;
  selectedChatId?: string;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

export default function Sidebar({ onNewChat, onSelectChat, selectedChatId, collapsed: controlledCollapsed, onToggleCollapse }: SidebarProps) {
  const navigate = useNavigate();
  const { isDark, toggleTheme } = useTheme();
  const [internalCollapsed, setInternalCollapsed] = useState(false);
  
  // 使用外部控制的 collapsed 或内部状态
  const collapsed = controlledCollapsed !== undefined ? controlledCollapsed : internalCollapsed;
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const profileButtonRef = useRef<HTMLButtonElement | null>(null);
  const profilePopoverRef = useRef<HTMLDivElement | null>(null);
  const [profile, setProfile] = useState<{ name: string; email: string }>({
    name: 'Temporary',
    email: 'user@example.com'
  });

  useEffect(() => {
    try {
      const saved = localStorage.getItem('userProfile');
      if (saved) {
        const parsed = JSON.parse(saved) as { name: string; email: string };
        if (parsed && parsed.name && parsed.email) {
          setProfile(parsed);
        }
      }
    } catch {}
  }, []);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      if (
        isProfileOpen &&
        profilePopoverRef.current &&
        !profilePopoverRef.current.contains(target) &&
        profileButtonRef.current &&
        !profileButtonRef.current.contains(target)
      ) {
        setIsProfileOpen(false);
      }
    };
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsProfileOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isProfileOpen]);

  const saveProfile = () => {
    try {
      localStorage.setItem('userProfile', JSON.stringify(profile));
      setIsProfileOpen(false);
    } catch {}
  };

  const initials = (name: string) => {
    const parts = name.trim().split(/\s+/);
    const letters = parts.slice(0, 2).map(p => p[0]?.toUpperCase() ?? 'U');
    return letters.join('') || 'U';
  };

  const handleChatClick = (chatId: string) => {
    onSelectChat(chatId);
    navigate(`/chat/${chatId}`);
  };

  const handleNewChatClick = () => {
    try {
      onNewChat();
    } finally {
      navigate('/');
    }
  };

  return (
    <div className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
      {/* Collapse control row */}
      <div className={styles.headerTop}>
        <button 
          className={styles.collapseBtn} 
          onClick={() => {
            if (onToggleCollapse) {
              onToggleCollapse();
            } else {
              setInternalCollapsed(v => !v);
            }
          }} 
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronsRight size={16} /> : <ChevronsLeft size={16} />}
        </button>
      </div>

      {/* New Chat row */}
      <div className={styles.header}>
        <button className={styles.newChatButton} onClick={handleNewChatClick}>
          <Plus size={16} />
          <span className={styles.label}>New chat</span>
        </button>
      </div>

      {/* Quick Links under New Chat */}
      <div className={styles.contentSection}>
        <div className={styles.contentItem} onClick={() => navigate('/knowledge')}>
          <Book size={16} />
          <span className={styles.label}>知识库</span>
        </div>
        <div className={styles.contentItem} onClick={() => navigate('/favorites')}>
          <Star size={16} />
          <span className={styles.label}>收藏</span>
        </div>
        <div className={styles.contentItem} onClick={() => navigate('/notes')}>
          <Notebook size={16} />
          <span className={styles.label}>笔记</span>
        </div>
      </div>

      {/* Chat List */}
      <div className={styles.chatList}>
        <div className={styles.sectionTitle}>近七天</div>
        {mockChats.filter(c => {
          const s = c.timestamp.toLowerCase();
          return s.includes('hour') || s.includes('day') && parseInt(s, 10) <= 7;
        }).map((chat) => (
          <div
            key={chat.id}
            className={`${styles.chatItem} ${selectedChatId === chat.id ? styles.selected : ''}`}
            onClick={() => handleChatClick(chat.id)}
          >
            <div className={styles.chatContent}>
              <div className={styles.chatTitle}>{chat.title}</div>
              <div className={styles.chatPreview}>{chat.lastMessage}</div>
            </div>
            <div className={styles.chatTime}>{chat.timestamp}</div>
          </div>
        ))}

        <div className={styles.sectionTitle}>更早</div>
        {mockChats.filter(c => {
          const s = c.timestamp.toLowerCase();
          if (s.includes('hour')) return false;
          const m = s.match(/(\d+)/);
          if (!m) return true;
          return parseInt(m[1], 10) > 7;
        }).map((chat) => (
          <div
            key={chat.id}
            className={`${styles.chatItem} ${selectedChatId === chat.id ? styles.selected : ''}`}
            onClick={() => handleChatClick(chat.id)}
          >
            <div className={styles.chatContent}>
              <div className={styles.chatTitle}>{chat.title}</div>
              <div className={styles.chatPreview}>{chat.lastMessage}</div>
            </div>
            <div className={styles.chatTime}>{chat.timestamp}</div>
          </div>
        ))}
      </div>

      {/* Bottom Section with Avatar */}
      <div className={styles.bottomSection}>
        <div className={styles.userRow}>
          <button
            ref={profileButtonRef}
            className={styles.avatarButton}
            onClick={() => setIsProfileOpen(v => !v)}
            aria-label="用户菜单"
          >
            <span className={styles.avatar}>{initials(profile.name)}</span>
          </button>
          <div className={styles.userMeta}>
            <div className={styles.userName}>{profile.name}</div>
            <div className={styles.userEmail}>{profile.email}</div>
          </div>
          {/* settings button removed as requested */}
        </div>
        {isProfileOpen && (
          <div ref={profilePopoverRef} className={styles.avatarPopover} role="dialog" aria-label="用户菜单">
            <div className={styles.menuList}>
              <button className={styles.menuItem} onClick={toggleTheme}>
                <span className={styles.menuIcon}>{isDark ? <Sun size={16} /> : <Moon size={16} />}</span>
                <span>{isDark ? '日间模式' : '夜间模式'}</span>
              </button>
              <button
                className={styles.menuItem}
                onClick={() => {
                  const link = document.createElement('a');
                  link.href = 'mailto:support@example.com?subject=Contact';
                  link.click();
                }}
              >
                <span className={styles.menuIcon}><Headphones size={16} /></span>
                <span>联系我们</span>
              </button>
              <button
                className={`${styles.menuItem} ${styles.menuDanger}`}
                onClick={() => {
                  try {
                    localStorage.removeItem('userProfile');
                    localStorage.removeItem('auth_token');
                    localStorage.removeItem('auth_user');
                  } catch {}
                  setIsProfileOpen(false);
                  navigate('/auth');
                }}
              >
                <span className={styles.menuIcon}><LogOut size={16} /></span>
                <span>退出登录</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Plus, Paperclip, Menu, Copy, RefreshCw, ThumbsUp, ThumbsDown } from 'lucide-react';
import Sidebar from '@/components/Sidebar/Sidebar';
import Header from '@/components/Header/Header';
import styles from './ChatDetail.module.css';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: string;
}

// Mock data for demonstration
const mockMessages: { [key: string]: Message[] } = {
  '1': [
    {
      id: '1',
      content: 'Help me fix typos in my document',
      sender: 'user',
      timestamp: '2 hours ago'
    },
    {
      id: '2',
      content: 'I\'d be happy to help you fix typos in your document. Please share the document or paste the text you\'d like me to review.',
      sender: 'assistant',
      timestamp: '2 hours ago'
    }
  ],
  '2': [
    {
      id: '1',
      content: 'Quadratic Function Plot',
      sender: 'user',
      timestamp: '1 day ago'
    },
    {
      id: '2',
      content: 'I can help you create a quadratic function plot. What specific quadratic function would you like to visualize? Please provide the equation in the form y = ax² + bx + c.',
      sender: 'assistant',
      timestamp: '1 day ago'
    }
  ]
};

const mockChatTitles: { [key: string]: string } = {
  '1': 'Typo Assistance Request',
  '2': 'Quadratic Function Plot',
  '3': 'Toyota Names Poetry',
  '4': 'Urban Green Spaces'
};

export default function ChatDetail() {
  const { chatId } = useParams<{ chatId: string }>();
  const navigate = useNavigate();
  const [inputMessage, setInputMessage] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const messageInputRef = useRef<HTMLTextAreaElement | null>(null);
  const [maxInputHeight, setMaxInputHeight] = useState<number>(240);
  const [mode, setMode] = useState<'deep' | 'search'>('deep');
  // profile UI moved to Sidebar
  
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // profile UI moved to Sidebar

  useEffect(() => {
    const updateMaxHeight = () => {
      const viewportHeight = window.innerHeight || 800;
      const computedMax = Math.max(160, Math.floor(viewportHeight * 0.4));
      setMaxInputHeight(computedMax);
    };
    updateMaxHeight();
    window.addEventListener('resize', updateMaxHeight);
    return () => window.removeEventListener('resize', updateMaxHeight);
  }, []);

  const autoResizeTextarea = (el?: HTMLTextAreaElement | null) => {
    const target = el ?? messageInputRef.current;
    if (!target) return;
    target.style.height = 'auto';
    const nextHeight = Math.min(target.scrollHeight, maxInputHeight);
    target.style.height = `${nextHeight}px`;
    target.style.overflowY = target.scrollHeight > maxInputHeight ? 'auto' : 'hidden';
  };

  // profile UI moved to Sidebar
  
  const messages = chatId ? mockMessages[chatId] || [] : [];
  const chatTitle = chatId ? mockChatTitles[chatId] || 'Chat' : 'Chat';

  const handleBack = () => {
    navigate('/');
  };

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      // TODO: Implement message sending logic
      console.log('Sending message:', inputMessage);
      setInputMessage('');
      if (messageInputRef.current) {
        messageInputRef.current.style.height = 'auto';
        messageInputRef.current.style.overflowY = 'hidden';
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={styles.chatDetail}>
      {/* Mobile Sidebar Overlay */}
      {isMobile && isSidebarOpen && (
        <div className={styles.overlay} onClick={() => setIsSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <div className={`${styles.sidebarContainer} ${isMobile && isSidebarOpen ? styles.open : ''}`}>
        <Sidebar
          onNewChat={() => navigate('/')}
          onSelectChat={(id: string) => navigate(`/chat/${id}`)}
          selectedChatId={chatId}
        />
      </div>

      {/* Main Content */}
      <div className={styles.mainContent}>
        {/* Header */}
        <header className={styles.header}>
          <div className={styles.headerLeft}>
            {isMobile && (
              <button
                className={styles.iconButton}
                onClick={() => setIsSidebarOpen(true)}
                aria-label="打开侧边栏"
              >
                <Menu size={20} />
              </button>
            )}
            <button 
              className={styles.backButton}
              onClick={handleBack}
              aria-label="返回"
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className={styles.title}>{chatTitle}</h1>
          </div>
          <div className={styles.headerRight}>
          </div>
        </header>

        {/* Messages Area */}
        <div className={styles.messagesContainer}>
          <div className={styles.messages}>
            {messages.length === 0 ? (
              <div className={styles.emptyState}>
                <p>开始新的对话</p>
              </div>
            ) : (
              messages.map((message) => (
              <div 
                key={message.id} 
                className={`${styles.message} ${
                  message.sender === 'user' ? styles.userMessage : styles.assistantMessage
                }`}
              >
                <div className={styles.messageContent}>
                  {message.content}
                </div>
                {message.sender === 'assistant' && (
                  <div className={styles.messageActions}>
                    <button
                      className={styles.actionButton}
                      onClick={async () => {
                        try { await navigator.clipboard.writeText(message.content); } catch {}
                      }}
                    >
                      <Copy size={14} />
                      
                    </button>
                    <button
                      className={styles.actionButton}
                      onClick={() => { console.log('regenerate', message.id); }}
                    >
                      <RefreshCw size={14} />
                      
                    </button>
                    <button
                      className={styles.actionButton}
                      onClick={() => { console.log('like', message.id); }}
                      aria-label="点赞"
                    >
                      <ThumbsUp size={14} />
                    </button>
                    <button
                      className={styles.actionButton}
                      onClick={() => { console.log('dislike', message.id); }}
                      aria-label="点灭"
                    >
                      <ThumbsDown size={14} />
                    </button>
                  </div>
                )}
              </div>
              ))
            )}
          </div>
        </div>

        {/* Input Area */}
        <div className={styles.inputContainer}>
          <div className={styles.inputWrapper}>
            <div className={styles.inputRow}>
              <button className={styles.attachButton} aria-label="附件">
                <Paperclip size={20} />
              </button>
              <textarea
                ref={messageInputRef}
                value={inputMessage}
                onChange={(e) => {
                  setInputMessage(e.target.value);
                  autoResizeTextarea(e.currentTarget);
                }}
                onKeyPress={handleKeyPress}
                placeholder={mode === 'deep' ? '输入问题开始深度思考...' : '输入关键词进行联网搜索...'}
                className={styles.messageInput}
                rows={1}
              />
            </div>
            <div className={styles.inputChipsInline}>
              <div className={styles.chipsGroup}>
                <button
                  className={`${styles.inputPill} ${mode === 'deep' ? styles.inputPillActive : ''}`}
                  onClick={() => setMode('deep')}
                  aria-pressed={mode === 'deep'}
                >深度思考</button>
                <button
                  className={`${styles.inputPill} ${mode === 'search' ? styles.inputPillActive : ''}`}
                  onClick={() => setMode('search')}
                  aria-pressed={mode === 'search'}
                >联网搜索</button>
              </div>
              <button 
                className={styles.sendButton}
                onClick={handleSendMessage}
                disabled={!inputMessage.trim()}
                aria-label="发送"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>


      </div>
    </div>
  );
}
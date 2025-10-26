import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '@/components/Sidebar/Sidebar';
import { ArrowLeft, Send, Menu, Copy, RefreshCw } from 'lucide-react';
import { useRAGChat } from '@/hooks/useRAGChat';
import { useToast } from '@/hooks/useToast';
import styles from './ChatDetail.module.css';

export default function ChatDetail() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const [chatMode, setChatMode] = useState<'deep' | 'search'>('deep');
  
  // RAG Chat Hook
  const { messages, isStreaming, sendMessage, regenerateLastMessage } = useRAGChat({
    mode: chatMode,
    onError: (error) => toast.error(`对话错误: ${error}`)
  });

  const handleSendMessage = () => {
    if (!inputMessage.trim() || isStreaming) return;
    sendMessage(inputMessage);
    setInputMessage('');
  };

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    toast.success('已复制到剪贴板');
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
          onSelectChat={(id) => navigate(`/chat/${id}`)}
          selectedChatId={chatId}
        />
      </div>

      {/* Main Content */}
      <div className={styles.mainContent}>
        {/* Header */}
        <div className={styles.header}>
          {isMobile && (
            <button onClick={() => setIsSidebarOpen(true)} className={styles.menuButton}>
              <Menu size={24} />
            </button>
          )}
          <button onClick={() => navigate('/')} className={styles.backButton}>
            <ArrowLeft size={20} />
          </button>
          <h1 className={styles.title}>对话详情</h1>
        </div>

        {/* Messages Area */}
        <div className={styles.messagesArea}>
          {messages.map((msg) => (
            <div 
              key={msg.id}
              className={msg.role === 'user' ? styles.userMessage : styles.aiMessage}
            >
              <div className={styles.messageContent}>{msg.content}</div>
              {msg.quotes && msg.quotes.length > 0 && (
                <div className={styles.quotes}>
                  {msg.quotes.map((quote: any, i: number) => (
                    <div key={i} className={styles.quoteCard}>
                      <div className={styles.quoteSource}>📄 {quote.source}</div>
                      {quote.page && <div className={styles.quotePage}>第 {quote.page} 页</div>}
                    </div>
                  ))}
                </div>
              )}
              {msg.role === 'assistant' && (
                <div className={styles.messageActions}>
                  <button onClick={() => handleCopyMessage(msg.content)} title="复制">
                    <Copy size={16} />
                  </button>
                  <button onClick={() => regenerateLastMessage()} title="重新生成">
                    <RefreshCw size={16} />
                  </button>
                </div>
              )}
            </div>
          ))}
          {isStreaming && (
            <div className={styles.streamingIndicator}>
              <div className={styles.loadingDots}>
                <span>.</span><span>.</span><span>.</span>
              </div>
              <span>AI 正在思考...</span>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className={styles.inputArea}>
          <div className={styles.modeSwitch}>
            <button 
              className={chatMode === 'deep' ? styles.modeActive : ''}
              onClick={() => setChatMode('deep')}
              disabled={isStreaming}
            >
              深度思考
            </button>
            <button 
              className={chatMode === 'search' ? styles.modeActive : ''}
              onClick={() => setChatMode('search')}
              disabled={isStreaming}
            >
              联网搜索
            </button>
          </div>
          <div className={styles.inputRow}>
            <input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
                  handleSendMessage();
                }
              }}
              placeholder="继续对话..."
              className={styles.input}
              disabled={isStreaming}
            />
            <button 
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isStreaming}
              className={styles.sendBtn}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}


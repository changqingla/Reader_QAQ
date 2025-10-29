import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '@/components/Sidebar/Sidebar';
import OptimizedMarkdown from '@/components/OptimizedMarkdown';
import { useRAGChat } from '@/hooks/useRAGChat';
import { useToast } from '@/hooks/useToast';
import { api } from '@/lib/api';
import { ArrowUp, Menu, User, Sparkles, Zap, Search, Database, X, Check } from 'lucide-react';
import styles from './Home.module.css';

export default function Home() {
  const toast = useToast();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [webSearch, setWebSearch] = useState(false);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [chatSessions, setChatSessions] = useState<any[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>(undefined);
  
  // 知识库选择相关状态
  const [showKBSelector, setShowKBSelector] = useState(false);
  const [selectedKBs, setSelectedKBs] = useState<string[]>([]);
  const [myKBs, setMyKBs] = useState<any[]>([]);
  const [favoriteKBs, setFavoriteKBs] = useState<any[]>([]);
  const [loadingKBs, setLoadingKBs] = useState(false);
  const kbSelectorRef = useRef<HTMLDivElement>(null);

  // 根据选择确定模式：深度思考固定启用，可选择联网搜索
  const chatMode = webSearch ? 'search' : 'deep';

  const { messages, isStreaming, isLoading, sendMessage, clearMessages, sessionId } = useRAGChat({
    sessionId: currentSessionId,
    mode: chatMode,
    disableQuotes: webSearch, // 联网搜索时禁用引用显示
    onError: (error) => toast.error(`对话错误: ${error}`),
    onSessionCreated: (newSessionId) => {
      setCurrentSessionId(newSessionId);
      loadChatSessions(); // 重新加载会话列表
    }
  });

  // 加载聊天会话列表
  const loadChatSessions = async () => {
    try {
      const response = await api.listChatSessions(1, 50);
      setChatSessions(response.sessions);
    } catch (error) {
      console.error('Failed to load chat sessions:', error);
    }
  };

  // 加载知识库
  const loadKnowledgeBases = async () => {
    setLoadingKBs(true);
    try {
      const [myKBResponse, favoriteKBResponse] = await Promise.all([
        api.listKnowledgeBases(undefined, 1, 50),
        api.listFavoriteKBs(1, 50)
      ]);
      setMyKBs(myKBResponse.items || []);
      setFavoriteKBs(favoriteKBResponse.items || []);
    } catch (error) {
      console.error('Failed to load knowledge bases:', error);
      toast.error('加载知识库失败');
    } finally {
      setLoadingKBs(false);
    }
  };

  // 切换知识库选择
  const toggleKBSelection = (kbId: string) => {
    setSelectedKBs(prev =>
      prev.includes(kbId)
        ? prev.filter(id => id !== kbId)
        : [...prev, kbId]
    );
  };

  // 打开知识库选择器时加载知识库
  const handleOpenKBSelector = () => {
    setShowKBSelector(true);
    if (myKBs.length === 0 && favoriteKBs.length === 0) {
      loadKnowledgeBases();
    }
  };

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth <= 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // 点击外部关闭知识库选择器
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (kbSelectorRef.current && !kbSelectorRef.current.contains(event.target as Node)) {
        setShowKBSelector(false);
      }
    };

    if (showKBSelector) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showKBSelector]);

  // 加载历史会话
  useEffect(() => {
    loadChatSessions();
  }, []);

  // 自动滚动到最新消息
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isStreaming]);

  const handleSend = () => {
    if (!inputMessage.trim() || isStreaming) return;
    sendMessage(inputMessage);
    setInputMessage('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickQuestions = [
    '总结《Attention is all you need》论文',
    '什么是 Transformer 架构？',
    '大语言模型的应用场景',
    'AI 在教育领域的应用',
    '如何提升模型推理速度？',
    '知识图谱与 LLM 的结合'
  ];

  // 新建对话
  const handleNewChat = () => {
    setCurrentSessionId(undefined);
    clearMessages();
  };

  // 选择历史会话
  const handleSelectChat = (chatId: string) => {
    if (chatId !== currentSessionId) {
      setCurrentSessionId(chatId);
      // useRAGChat 会自动检测到 sessionId 变化并加载历史消息
    }
  };

  // 删除会话
  const handleDeleteChat = async (chatId: string) => {
    try {
      await api.deleteChatSession(chatId);
      // 如果删除的是当前会话，切换到新对话
      if (chatId === currentSessionId) {
        handleNewChat();
      }
      // 重新加载会话列表
      await loadChatSessions();
      toast.success('对话已删除');
    } catch (error) {
      console.error('Failed to delete chat:', error);
      toast.error('删除对话失败');
    }
  };

  return (
    <div className={styles.home}>
      {isMobile && isSidebarOpen && (
        <div className={styles.overlay} onClick={() => setIsSidebarOpen(false)} />
      )}
      
      <div className={`${styles.sidebarContainer} ${isMobile && isSidebarOpen ? styles.open : ''}`}>
        <Sidebar
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
          selectedChatId={currentSessionId}
          chats={chatSessions}
        />
      </div>

      <div className={styles.mainContent}>
        {isMobile && (
          <div className={styles.mobileHeader}>
            <button onClick={() => setIsSidebarOpen(true)} className={styles.menuButton}>
              <Menu size={20} />
            </button>
            <h1 className={styles.mobileTitle}>Reader QAQ</h1>
          </div>
        )}
        
        <div className={styles.chatContainer}>
          {isLoading ? (
            // 加载历史消息
            <div className={styles.loadingContainer}>
              <div className={styles.loadingSpinner}></div>
              <p className={styles.loadingText}>加载历史消息...</p>
            </div>
          ) : messages.length === 0 ? (
            // 欢迎屏幕 + 居中输入框
            <div className={styles.emptyContainer}>
              <div className={`${styles.welcomeContent} ${styles.welcomeCompact}`}>
                <h1 className={styles.welcomeTitle}>
                  用<span className={styles.highlight}>提问</span>发现世界
                </h1>

                <div className={styles.suggestions}>
                  {quickQuestions.map((q, i) => (
                    <button
                      key={i}
                      className={styles.suggestionTag}
                      onClick={() => setInputMessage(q)}
                      disabled={isStreaming}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>

              <div className={`${styles.inputSection} ${styles.centeredInputSection}`}>
                <div className={styles.inputWrapper}>
                  <div className={styles.inputBox}>
                    <div className={styles.inputRow}>
                      <textarea
                        className={styles.input}
                        placeholder="输入您的问题..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={isStreaming}
                        rows={1}
                        style={{
                          height: 'auto',
                          minHeight: '24px',
                          maxHeight: '200px'
                        }}
                        onInput={(e) => {
                          const target = e.target as HTMLTextAreaElement;
                          target.style.height = 'auto';
                          target.style.height = target.scrollHeight + 'px';
                        }}
                      />
                      <div className={styles.inputActions}>
                        <button
                          className={`${styles.iconButton} ${styles.sendButton}`}
                          onClick={handleSend}
                          disabled={!inputMessage.trim() || isStreaming}
                          title="发送"
                        >
                          <ArrowUp size={22} strokeWidth={2.5} />
                        </button>
                      </div>
                    </div>

                    <div className={styles.modeSwitch}>
                      <button
                        className={`${styles.modeButton} ${!webSearch ? styles.active : ''}`}
                        disabled={true}
                        title="深度思考默认启用"
                      >
                        <Zap size={16} />
                        <span>深度思考</span>
                      </button>
                      <button
                        className={`${styles.modeButton} ${webSearch ? styles.active : ''}`}
                        onClick={() => setWebSearch(!webSearch)}
                        disabled={isStreaming}
                        title="联网搜索"
                      >
                        <Search size={16} />
                        <span>联网搜索</span>
                      </button>
                      <div className={styles.kbSelectorWrapper} ref={kbSelectorRef}>
                        <button
                          className={`${styles.modeButton} ${selectedKBs.length > 0 ? styles.active : ''}`}
                          onClick={handleOpenKBSelector}
                          disabled={isStreaming}
                          title="选择知识库"
                        >
                          <Database size={16} />
                          <span>知识库{selectedKBs.length > 0 && ` (${selectedKBs.length})`}</span>
                        </button>
                        
                        {showKBSelector && (
                          <div className={styles.kbSelectorPanel}>
                            {loadingKBs ? (
                              <div className={styles.kbSelectorLoading}>加载中...</div>
                            ) : (
                              <div className={styles.kbSelectorContent}>
                                {myKBs.length > 0 && (
                                  <div className={styles.kbSection}>
                                    <div className={styles.kbSectionTitle}>我的知识库</div>
                                    {myKBs.map((kb) => (
                                      <label key={kb.id} className={styles.kbItem}>
                                        <input
                                          type="checkbox"
                                          checked={selectedKBs.includes(kb.id)}
                                          onChange={() => toggleKBSelection(kb.id)}
                                          className={styles.kbCheckbox}
                                        />
                                        <div className={styles.kbItemContent}>
                                          <img src={kb.avatar} alt={kb.name} className={styles.kbAvatar} />
                                          <span className={styles.kbName}>{kb.name}</span>
                                        </div>
                                        {selectedKBs.includes(kb.id) && (
                                          <Check size={16} className={styles.kbCheckIcon} />
                                        )}
                                      </label>
                                    ))}
                                  </div>
                                )}

                                {favoriteKBs.length > 0 && (
                                  <div className={styles.kbSection}>
                                    <div className={styles.kbSectionTitle}>收藏的知识库</div>
                                    {favoriteKBs.map((kb) => (
                                      <label key={kb.id} className={styles.kbItem}>
                                        <input
                                          type="checkbox"
                                          checked={selectedKBs.includes(kb.id)}
                                          onChange={() => toggleKBSelection(kb.id)}
                                          className={styles.kbCheckbox}
                                        />
                                        <div className={styles.kbItemContent}>
                                          <img src={kb.avatar} alt={kb.name} className={styles.kbAvatar} />
                                          <span className={styles.kbName}>{kb.name}</span>
                                        </div>
                                        {selectedKBs.includes(kb.id) && (
                                          <Check size={16} className={styles.kbCheckIcon} />
                                        )}
                                      </label>
                                    ))}
                                  </div>
                                )}

                                {myKBs.length === 0 && favoriteKBs.length === 0 && !loadingKBs && (
                                  <div className={styles.kbSelectorEmpty}>暂无可用知识库</div>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className={styles.disclaimer}>
                    答案由AI生成，AI也会犯错
                  </div>
                </div>
              </div>
            </div>
          ) : (
            // 对话界面
            <>
              <div className={styles.messagesArea}>
                <div className={styles.messageGroup}>
                  {messages.map((msg, index) => (
                    <div key={msg.id} className={`${styles.messageItem} ${msg.role === 'user' ? styles.userMessageItem : styles.aiMessageItem}`}>
                      <div className={msg.role === 'user' ? styles.userAvatar : styles.aiAvatar}>
                        {msg.role === 'user' ? <User size={18} /> : <Sparkles size={18} />}
                      </div>
                      <div className={styles.messageContent}>
                        {/* 如果是 AI 消息且内容为空且正在流式传输（最后一条消息），显示思考动画 */}
                        {msg.role === 'assistant' && !msg.content && isStreaming && index === messages.length - 1 ? (
                          <div className={styles.thinking}>
                            <div className={styles.thinkingDots}>
                              <span className={styles.dot}></span>
                              <span className={styles.dot}></span>
                              <span className={styles.dot}></span>
                            </div>
                            <span className={styles.thinkingText}>正在思考...</span>
                          </div>
                        ) : (
                          <>
                              <div className={msg.role === 'user' ? styles.userMessageText : styles.aiMessageText}>
                                {msg.role === 'user' ? (
                                  msg.content
                                ) : (
                                  <OptimizedMarkdown>
                                    {msg.content}
                                  </OptimizedMarkdown>
                                )}
                              </div>
                            {msg.quotes && msg.quotes.length > 0 && (
                              <div className={styles.quotes}>
                                {msg.quotes.map((quote: any, i: number) => (
                                  <div key={i} className={styles.quote}>
                                    <div className={styles.quoteSource}>📄 {quote.source}</div>
                                    {quote.page && (
                                      <div className={styles.quotePage}>第 {quote.page} 页</div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              </div>

              <div className={styles.inputSection}>
                <div className={styles.inputWrapper}>
                  <div className={styles.inputBox}>
                    <div className={styles.inputRow}>
                      <textarea
                        className={styles.input}
                        placeholder="继续对话..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={isStreaming}
                        rows={1}
                        style={{
                          height: 'auto',
                          minHeight: '24px',
                          maxHeight: '200px'
                        }}
                        onInput={(e) => {
                          const target = e.target as HTMLTextAreaElement;
                          target.style.height = 'auto';
                          target.style.height = target.scrollHeight + 'px';
                        }}
                      />
                      <div className={styles.inputActions}>
                        <button
                          className={`${styles.iconButton} ${styles.sendButton}`}
                          onClick={handleSend}
                          disabled={!inputMessage.trim() || isStreaming}
                          title="发送"
                        >
                          <ArrowUp size={22} strokeWidth={2.5} />
                        </button>
                      </div>
                    </div>

                    <div className={styles.modeSwitch}>
                      <button
                        className={`${styles.modeButton} ${!webSearch ? styles.active : ''}`}
                        disabled={true}
                        title="深度思考默认启用"
                      >
                        <Zap size={16} />
                        <span>深度思考</span>
                      </button>
                      <button
                        className={`${styles.modeButton} ${webSearch ? styles.active : ''}`}
                        onClick={() => setWebSearch(!webSearch)}
                        disabled={isStreaming}
                        title="联网搜索"
                      >
                        <Search size={16} />
                        <span>联网搜索</span>
                      </button>
                      <button
                        className={`${styles.modeButton} ${selectedKBs.length > 0 ? styles.active : ''}`}
                        onClick={handleOpenKBSelector}
                        disabled={isStreaming}
                        title="选择知识库"
                      >
                        <Database size={16} />
                        <span>知识库{selectedKBs.length > 0 && ` (${selectedKBs.length})`}</span>
                      </button>
                    </div>
                  </div>
                  
                  <div className={styles.disclaimer}>
                    答案由AI生成，AI也会犯错
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

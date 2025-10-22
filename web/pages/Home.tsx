import React, { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar/Sidebar';
import Header from '@/components/Header/Header';
import ChatArea from '@/components/ChatArea/ChatArea';
import InputArea from '@/components/InputArea/InputArea';
import styles from './Home.module.css';

export default function Home() {
  const [selectedChatId, setSelectedChatId] = useState<string | undefined>();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleNewChat = () => {
    setSelectedChatId(undefined);
    if (isMobile) {
      setIsSidebarOpen(false);
    }
  };

  const handleSelectChat = (chatId: string) => {
    setSelectedChatId(chatId);
    if (isMobile) {
      setIsSidebarOpen(false);
    }
  };

  const handleSendMessage = (message: string) => {
    console.log('Sending message:', message);
    // TODO: Implement message sending logic
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className={styles.home}>
      {/* Mobile Sidebar Overlay */}
      {isMobile && isSidebarOpen && (
        <div className={styles.overlay} onClick={() => setIsSidebarOpen(false)} />
      )}
      
      {/* Sidebar */}
      <div className={`${styles.sidebarContainer} ${isMobile && isSidebarOpen ? styles.open : ''}`}>
        <Sidebar
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
          selectedChatId={selectedChatId}
        />
      </div>

      {/* Main Content */}
      <div className={styles.mainContent}>
        <Header 
          onToggleSidebar={toggleSidebar}
          isMobile={isMobile}
        />
        
        <div className={styles.chatContainer}>
          <ChatArea selectedChatId={selectedChatId} />
          {selectedChatId && (
            <InputArea onSendMessage={handleSendMessage} />
          )}
        </div>
      </div>
    </div>
  );
}
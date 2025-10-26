import { useState, useCallback, useRef, useEffect } from 'react';
import { ragAPI } from '@/lib/rag-api';
import { api } from '@/lib/api';
import { generateUUID } from '@/lib/uuid';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  quotes?: Array<{
    source: string;
    page?: number;
  }>;
}

interface UseRAGChatOptions {
  sessionId?: string; // 已存在的会话ID
  kbId?: string;
  docIds?: string[];
  mode?: 'deep' | 'search';
  disableQuotes?: boolean; // 是否禁用引用显示（联网搜索时）
  onError?: (error: string) => void;
  onSessionCreated?: (sessionId: string) => void; // 新会话创建时的回调
}

export function useRAGChat(options: UseRAGChatOptions = {}) {
  const { sessionId: externalSessionId, kbId, docIds, mode = 'deep', disableQuotes = false, onError, onSessionCreated } = options;
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const sessionIdRef = useRef<string | null>(externalSessionId || null);
  const currentMessageRef = useRef<Message | null>(null);

  // 加载历史消息
  useEffect(() => {
    if (externalSessionId && externalSessionId !== sessionIdRef.current) {
      sessionIdRef.current = externalSessionId;
      loadMessages(externalSessionId);
    } else if (!externalSessionId && sessionIdRef.current) {
      // 如果 externalSessionId 被清空（新对话），清空消息
      sessionIdRef.current = null;
      setMessages([]);
    }
  }, [externalSessionId]);

  const loadMessages = async (sessionId: string) => {
    try {
      setIsLoading(true);
      const response = await api.getChatMessages(sessionId);
      const loadedMessages: Message[] = response.messages.map(msg => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        quotes: msg.quotes
      }));
      setMessages(loadedMessages);
    } catch (error) {
      console.error('Failed to load messages:', error);
      onError?.('加载历史消息失败');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isStreaming) return;

    try {
      // 如果没有会话ID，先创建会话
      if (!sessionIdRef.current) {
        const session = await api.createChatSession(content);
        sessionIdRef.current = session.id;
        onSessionCreated?.(session.id);
      }

      // Add user message to UI
      const userMessage: Message = {
        id: generateUUID(),
        role: 'user',
        content
      };
      setMessages(prev => [...prev, userMessage]);

      // Save user message to database
      await api.addChatMessage(sessionIdRef.current, 'user', content, mode);

      // Create assistant message placeholder
      const assistantMessage: Message = {
        id: generateUUID(),
        role: 'assistant',
        content: '',
        quotes: []
      };
      currentMessageRef.current = assistantMessage;
      setMessages(prev => [...prev, assistantMessage]);

      setIsStreaming(true);

      // Stream RAG response
      await ragAPI.streamChat({
        kb_id: kbId,
        doc_ids: docIds,
        message: content,
        session_id: sessionIdRef.current,
        mode,
        onToken: (token) => {
          if (currentMessageRef.current) {
            currentMessageRef.current.content += token;
            setMessages(prev => [...prev.slice(0, -1), { ...currentMessageRef.current! }]);
          }
        },
        onQuote: (quote) => {
          if (!disableQuotes && currentMessageRef.current) {
            if (!currentMessageRef.current.quotes) {
              currentMessageRef.current.quotes = [];
            }
            currentMessageRef.current.quotes.push(quote);
            setMessages(prev => [...prev.slice(0, -1), { ...currentMessageRef.current! }]);
          }
        },
        onError: (error) => {
          onError?.(error);
          setIsStreaming(false);
        },
        onDone: async () => {
          setIsStreaming(false);
          // Save assistant message to database
          if (currentMessageRef.current && sessionIdRef.current) {
            try {
              await api.addChatMessage(
                sessionIdRef.current,
                'assistant',
                currentMessageRef.current.content,
                mode,
                currentMessageRef.current.quotes
              );
            } catch (error) {
              console.error('Failed to save assistant message:', error);
            }
          }
          currentMessageRef.current = null;
        }
      });
    } catch (error) {
      onError?.(String(error));
      setIsStreaming(false);
      // Remove the empty assistant message on error
      setMessages(prev => prev.slice(0, -1));
    }
  }, [kbId, docIds, mode, isStreaming, onError, onSessionCreated]);

  const regenerateLastMessage = useCallback(async () => {
    if (messages.length < 2) return;

    // Get the last user message
    const lastUserMessage = messages.slice().reverse().find(m => m.role === 'user');
    if (!lastUserMessage) return;

    // Remove the last assistant message
    setMessages(prev => prev.slice(0, -1));

    // Resend the message
    await sendMessage(lastUserMessage.content);
  }, [messages, sendMessage]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    sessionIdRef.current = null;
    currentMessageRef.current = null;
  }, []);

  return {
    messages,
    isStreaming,
    isLoading,
    sendMessage,
    regenerateLastMessage,
    clearMessages,
    sessionId: sessionIdRef.current
  };
}


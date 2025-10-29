import { API_BASE_URL } from './api';

interface ChatRequest {
  kb_id?: string;
  doc_ids?: string[];
  message: string;
  session_id: string;
  mode: 'deep' | 'search';
}

interface StreamChatOptions extends ChatRequest {
  onToken: (token: string) => void;
  onQuote: (quote: any) => void;
  onError: (error: string) => void;
  onDone: () => void;
}

class RAGAPIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Stream chat with RAG service
   */
  async streamChat(options: StreamChatOptions): Promise<void> {
    const { onToken, onQuote, onError, onDone, ...request } = options;

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${this.baseURL}/rag/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        // 处理401 Unauthorized错误（Token过期）
        if (response.status === 401) {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('userProfile');
          setTimeout(() => {
            window.location.href = '/auth';
          }, 1500);
          throw new Error('当前登录已过期，请重新登录');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim() || !line.startsWith('data: ')) continue;
          
          const data = line.slice(6); // Remove "data: " prefix
          
          if (data === '[DONE]') {
            onDone();
            return;
          }

          try {
            const chunk = JSON.parse(data);
            
            switch (chunk.type) {
              case 'token':
                onToken(chunk.content);
                break;
              case 'quote':
                if (chunk.quote) {
                  onQuote(chunk.quote);
                }
                break;
              case 'error':
                onError(chunk.content);
                return;
            }
          } catch (e) {
            console.warn('Failed to parse chunk:', data, e);
          }
        }
      }

      onDone();
    } catch (error) {
      onError(String(error));
    }
  }

  /**
   * Non-streaming chat (for testing)
   */
  async chat(request: ChatRequest): Promise<any> {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${this.baseURL}/rag/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      // 处理401 Unauthorized错误（Token过期）
      if (response.status === 401) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('userProfile');
        setTimeout(() => {
          window.location.href = '/auth';
        }, 1500);
        throw new Error('当前登录已过期，请重新登录');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }
}

export const ragAPI = new RAGAPIClient();


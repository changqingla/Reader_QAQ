// API 客户端工具
// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// 通用请求函数
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('auth_token');
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // 添加 Authorization header（如果有 token）
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    // 处理错误响应
    // FastAPI HTTPException 会包装在 detail 中
    const error = data.detail?.error || data.error || data;
    const errorMessage = error.message || '请求失败';
    
    // 根据错误码提供更友好的提示
    if (error.code === 'UNAUTHORIZED') {
      throw new Error(errorMessage || '账号或密码不正确');
    } else if (error.code === 'NOT_FOUND') {
      throw new Error(errorMessage || '账号未注册');
    } else if (error.code === 'CONFLICT') {
      throw new Error(errorMessage || '该邮箱已被注册');
    } else if (error.code === 'VALIDATION_ERROR') {
      throw new Error(errorMessage);
    } else {
      throw new Error(errorMessage);
    }
  }
  
  return data;
}

// 认证相关 API
export const authAPI = {
  /**
   * 用户登录
   */
  async login(email: string, password: string) {
    return request<{ token: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },
  
  /**
   * 用户注册
   */
  async register(email: string, password: string, name: string) {
    return request<{ token: string; user: any }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
  },
  
  /**
   * 获取当前用户信息
   */
  async getMe() {
    return request<{ id: string; name: string; email: string; avatar: string | null }>('/auth/me', {
      method: 'GET',
    });
  },
};

// 知识库相关 API
export const kbAPI = {
  /**
   * 列出知识库
   */
  async listKnowledgeBases(query?: string, page: number = 1, pageSize: number = 20) {
    const params = new URLSearchParams({ page: page.toString(), pageSize: pageSize.toString() });
    if (query) params.append('q', query);
    return request<{ total: number; page: number; pageSize: number; items: any[] }>(
      `/kb?${params}`,
      { method: 'GET' }
    );
  },

  /**
   * 创建知识库
   */
  async createKnowledgeBase(name: string, description: string, tags: string[]) {
    return request<{ id: string }>('/kb', {
      method: 'POST',
      body: JSON.stringify({ name, description, tags }),
    });
  },

  /**
   * 更新知识库
   */
  async updateKnowledgeBase(kbId: string, data: { name?: string; description?: string; tags?: string[] }) {
    return request<{ success: boolean }>(`/kb/${kbId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * 删除知识库
   */
  async deleteKnowledgeBase(kbId: string) {
    return request<{ success: boolean }>(`/kb/${kbId}`, {
      method: 'DELETE',
    });
  },

  /**
   * 获取存储配额
   */
  async getQuota() {
    return request<{ usedBytes: number; limitBytes: number }>('/kb/quota', {
      method: 'GET',
    });
  },

  /**
   * 上传文档
   */
  async uploadDocument(kbId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE_URL}/kb/${kbId}/documents`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      const error = data.detail?.error || data.error || data;
      throw new Error(error.message || '上传失败');
    }

    return data;
  },

  /**
   * 列出文档
   */
  async listDocuments(kbId: string, page: number = 1, pageSize: number = 20) {
    const params = new URLSearchParams({ page: page.toString(), pageSize: pageSize.toString() });
    return request<{ total: number; page: number; pageSize: number; items: any[] }>(
      `/kb/${kbId}/documents?${params}`,
      { method: 'GET' }
    );
  },

  /**
   * 获取文档处理状态
   */
  async getDocumentStatus(kbId: string, docId: string) {
    return request<{ status: string; errorMessage: string | null; chunkCount: number }>(
      `/kb/${kbId}/documents/${docId}/status`,
      { method: 'GET' }
    );
  },

  /**
   * 删除文档
   */
  async deleteDocument(kbId: string, docId: string) {
    return request<{ success: boolean }>(`/kb/${kbId}/documents/${docId}`, {
      method: 'DELETE',
    });
  },

  /**
   * 在知识库中检索
   */
  async searchInKB(kbId: string, question: string, topN: number = 10) {
    return request<{ messageId: string; references: any[]; answer: string }>(
      `/kb/${kbId}/chat/messages`,
      {
        method: 'POST',
        body: JSON.stringify({ question, top_n: topN }),
      }
    );
  },
};

// 笔记相关 API (TODO)
export const noteAPI = {
  // TODO: 实现笔记相关 API 调用
};

// 收藏相关 API (TODO)
export const favoriteAPI = {
  // TODO: 实现收藏相关 API 调用
};


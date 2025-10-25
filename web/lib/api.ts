// API 客户端工具
// API 基础配置
// 开发环境使用相对路径，通过 Vite 代理
// 生产环境使用环境变量配置的完整 URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

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
  async createKnowledgeBase(name: string, description: string, category: string = "其它") {
    return request<{ id: string }>('/kb', {
      method: 'POST',
      body: JSON.stringify({ name, description, category }),
    });
  },

  /**
   * 获取知识库信息（支持自己的和公开的）
   */
  async getKnowledgeBaseInfo(kbId: string) {
    return request<{
      id: string;
      name: string;
      description: string;
      category: string;
      isPublic: boolean;
      subscribersCount: number;
      viewCount: number;
      contents: number;
      avatar: string;
      createdAt: string;
      updatedAt: string;
      ownerId?: string;
      isOwner: boolean;
      isSubscribed: boolean;
    }>(`/kb/${kbId}/info`, {
      method: 'GET',
    });
  },

  /**
   * 更新知识库
   */
  async updateKnowledgeBase(kbId: string, data: { name?: string; description?: string; category?: string }) {
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

  /**
   * 获取文档预览 URL
   */
  async getDocumentUrl(kbId: string, docId: string) {
    return request<{ url: string; name: string }>(`/kb/${kbId}/documents/${docId}/url`, {
      method: 'GET',
    });
  },

  /**
   * 上传知识库头像
   */
  async uploadAvatar(kbId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE_URL}/kb/${kbId}/avatar`, {
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

  // ============ 公开共享 & 订阅功能 ============

  /**
   * 切换知识库公开/私有状态
   */
  async togglePublic(kbId: string) {
    return request<{ isPublic: boolean; subscribersCount: number }>(`/kb/${kbId}/toggle-public`, {
      method: 'POST',
    });
  },

  /**
   * 订阅公开知识库
   */
  async subscribe(kbId: string) {
    return request<{ subscribersCount: number }>(`/kb/${kbId}/subscribe`, {
      method: 'POST',
    });
  },

  /**
   * 取消订阅知识库
   */
  async unsubscribe(kbId: string) {
    return request<{ subscribersCount: number }>(`/kb/${kbId}/subscribe`, {
      method: 'DELETE',
    });
  },

  /**
   * 检查订阅状态
   */
  async checkSubscription(kbId: string) {
    return request<{ isSubscribed: boolean; subscribedAt: string | null }>(`/kb/${kbId}/subscription-status`, {
      method: 'GET',
    });
  },

  /**
   * 获取我的订阅列表
   */
  async listSubscriptions(page: number = 1, pageSize: number = 20) {
    const params = new URLSearchParams({ page: page.toString(), pageSize: pageSize.toString() });
    return request<{ total: number; page: number; pageSize: number; items: any[] }>(
      `/kb/subscriptions/list?${params}`,
      { method: 'GET' }
    );
  },

  /**
   * 获取公开知识库列表
   */
  async listPublicKBs(category?: string, query?: string, page: number = 1, pageSize: number = 20) {
    const params = new URLSearchParams({ page: page.toString(), pageSize: pageSize.toString() });
    if (category) params.append('category', category);
    if (query) params.append('q', query);
    return request<{ total: number; page: number; pageSize: number; items: any[] }>(
      `/kb/public/list?${params}`,
      { method: 'GET' }
    );
  },

  /**
   * 获取精选知识库列表（2025年度精选）
   */
  async listFeatured(page: number = 1, pageSize: number = 30) {
    const params = new URLSearchParams({ page: page.toString(), pageSize: pageSize.toString() });
    return request<{ total: number; page: number; pageSize: number; items: any[] }>(
      `/kb/featured/list?${params}`,
      { method: 'GET' }
    );
  },

  /**
   * 获取分类统计
   */
  async getCategoriesStats() {
    return request<{ categories: Array<{ category: string; count: number; subscribers: number }> }>(
      '/kb/categories/stats',
      { method: 'GET' }
    );
  },
};

// 笔记相关 API
export const noteAPI = {
  /**
   * 列出文件夹
   */
  async listFolders() {
    const response = await request<{ folders: Array<{ id: string; name: string; noteCount: number; createdAt: string }> }>(
      '/notes/folders',
      { method: 'GET' }
    );
    // 转换为前端期望的格式
    return response.folders.map(f => ({
      id: f.id,
      name: f.name,
      count: f.noteCount
    }));
  },

  /**
   * 创建文件夹
   */
  async createFolder(name: string) {
    return request<{ id: string; name: string }>('/notes/folders', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  },

  /**
   * 重命名文件夹
   */
  async renameFolder(folderId: string, name: string) {
    return request<{ success: boolean }>(`/notes/folders/${folderId}`, {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    });
  },

  /**
   * 删除文件夹
   */
  async deleteFolder(folderId: string) {
    return request<{ success: boolean }>(`/notes/folders/${folderId}`, {
      method: 'DELETE',
    });
  },

  /**
   * 列出笔记
   */
  async listNotes(folderId?: string, query?: string, page: number = 1, pageSize: number = 50) {
    const params = new URLSearchParams({ page: page.toString(), pageSize: pageSize.toString() });
    if (folderId) params.append('folderId', folderId);
    if (query) params.append('query', query);
    return request<{ total: number; page: number; pageSize: number; items: any[] }>(
      `/notes?${params}`,
      { method: 'GET' }
    );
  },

  /**
   * 获取笔记详情
   */
  async getNote(noteId: string) {
    return request<{ id: string; title: string; content: string; folderId: string | null; createdAt: string; updatedAt: string }>(
      `/notes/${noteId}`,
      { method: 'GET' }
    );
  },

  /**
   * 创建笔记
   */
  async createNote(data: { title: string; content?: string; folder?: string; tags?: string[] }) {
    return request<any>(
      '/notes',
      {
        method: 'POST',
        body: JSON.stringify({ 
          title: data.title, 
          content: data.content || '', 
          folder: data.folder || null,
          tags: data.tags || []
        }),
      }
    );
  },

  /**
   * 更新笔记
   */
  async updateNote(noteId: string, data: { title?: string; content?: string; folderId?: string | null }) {
    return request<any>(`/notes/${noteId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * 删除笔记
   */
  async deleteNote(noteId: string) {
    return request<{ success: boolean }>(`/notes/${noteId}`, {
      method: 'DELETE',
    });
  },
};

// 收藏相关 API
export const favoriteAPI = {
  /**
   * 收藏知识库
   */
  async favoriteKB(kbId: string) {
    return request<{ success: boolean }>(`/favorites/kb/${kbId}`, {
      method: 'POST',
    });
  },

  /**
   * 取消收藏知识库
   */
  async unfavoriteKB(kbId: string) {
    return request<{ success: boolean }>(`/favorites/kb/${kbId}`, {
      method: 'DELETE',
    });
  },

  /**
   * 获取收藏的知识库列表
   */
  async listFavoriteKBs(page: number = 1, pageSize: number = 20) {
    const params = new URLSearchParams({ page: page.toString(), pageSize: pageSize.toString() });
    return request<{ total: number; page: number; pageSize: number; items: any[] }>(
      `/favorites/kb?${params}`,
      { method: 'GET' }
    );
  },

  /**
   * 收藏文档
   */
  async favoriteDocument(docId: string, kbId: string) {
    const params = new URLSearchParams({ kbId });
    return request<{ success: boolean }>(`/favorites/document/${docId}?${params}`, {
      method: 'POST',
    });
  },

  /**
   * 取消收藏文档
   */
  async unfavoriteDocument(docId: string) {
    return request<{ success: boolean }>(`/favorites/document/${docId}`, {
      method: 'DELETE',
    });
  },

  /**
   * 获取收藏的文档列表
   */
  async listFavoriteDocuments(page: number = 1, pageSize: number = 20) {
    const params = new URLSearchParams({ page: page.toString(), pageSize: pageSize.toString() });
    return request<{ total: number; page: number; pageSize: number; items: any[] }>(
      `/favorites/document?${params}`,
      { method: 'GET' }
    );
  },

  /**
   * 批量检查收藏状态
   */
  async checkFavorites(items: Array<{ type: string; id: string }>) {
    return request<{ [key: string]: boolean }>('/favorites/check', {
      method: 'POST',
      body: JSON.stringify({ items }),
    });
  },
};


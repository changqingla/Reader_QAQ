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

// 笔记相关 API (TODO)
export const noteAPI = {
  // TODO: 实现笔记相关 API 调用
};

// 收藏相关 API (TODO)
export const favoriteAPI = {
  // TODO: 实现收藏相关 API 调用
};

// 知识库相关 API (TODO)
export const kbAPI = {
  // TODO: 实现知识库相关 API 调用
};


# 前端环境变量配置

## 创建配置文件

在项目根目录创建 `.env` 文件：

```bash
# .env
VITE_API_URL=http://localhost:8000/api
```

## 配置说明

### 开发环境
```
VITE_API_URL=http://localhost:8000/api
```

### 生产环境
```
VITE_API_URL=https://your-domain.com/api
```

## 使用方法

环境变量会在 `web/lib/api.ts` 中自动读取：

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

如果未配置环境变量，默认使用 `http://localhost:8000/api`。

## 重要提示

⚠️ `.env` 文件已在 `.gitignore` 中，不会被提交到 Git。
⚠️ 修改 `.env` 后需要重启前端开发服务器。


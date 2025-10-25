# 📄 PDF 预览功能实现说明

**实现时间**: 2025-10-25  
**状态**: ✅ 完成

---

## 🎯 功能概述

在知识库详情页中，用户可以点击文档列表中的文件来预览 PDF 内容。预览器会替换右侧的聊天区域，提供流畅的文档查看体验。

---

## ✨ 功能特性

### 1. **点击预览**
- ✅ 点击文档列表中状态为 `ready` 的文件
- ✅ 文件名和状态提示"点击预览"
- ✅ 点击后文档行高亮显示（蓝色边框）

### 2. **预览界面**
- ✅ 预览头部显示文档名称
- ✅ 收藏按钮（可快速收藏正在预览的文档）
- ✅ 关闭预览按钮
- ✅ 全屏 iframe 显示 PDF 内容

### 3. **加载状态**
- ✅ 加载中显示旋转的加载图标
- ✅ 加载失败显示错误提示
- ✅ 加载成功显示完整的 PDF 内容

### 4. **交互优化**
- ✅ 点击收藏/删除按钮时不触发预览
- ✅ 关闭预览后返回聊天界面
- ✅ 当前预览的文档在列表中高亮

---

## 🔧 技术实现

### 状态管理

```typescript
// PDF Preview State
const [previewDoc, setPreviewDoc] = useState<any>(null);         // 当前预览的文档
const [previewUrl, setPreviewUrl] = useState<string>('');        // 预览 URL
const [loadingPreview, setLoadingPreview] = useState(false);     // 加载状态
```

### 核心函数

#### 1. 预览文档
```typescript
const handlePreviewDocument = async (doc: any) => {
  if (!kbId) return;
  
  setLoadingPreview(true);
  setPreviewDoc(doc);
  
  try {
    const response = await kbAPI.getDocumentUrl(kbId, doc.id);
    setPreviewUrl(response.url);
  } catch (error: any) {
    toast.error(error.message || '无法加载文档预览');
    setPreviewDoc(null);
  } finally {
    setLoadingPreview(false);
  }
};
```

#### 2. 关闭预览
```typescript
const handleClosePreview = () => {
  setPreviewDoc(null);
  setPreviewUrl('');
};
```

### UI 组件结构

```jsx
<section className={styles.chatArea}>
  {previewDoc ? (
    // PDF 预览器
    <div className={styles.previewContainer}>
      <div className={styles.previewHeader}>
        <div className={styles.previewTitle}>
          <FileText size={18} />
          <span>{previewDoc.name}</span>
        </div>
        <div className={styles.previewActions}>
          <button onClick={() => handleToggleFavoriteDoc(previewDoc.id)}>
            收藏
          </button>
          <button onClick={handleClosePreview}>
            关闭预览
          </button>
        </div>
      </div>
      <div className={styles.previewContent}>
        {loadingPreview ? (
          <div className={styles.previewLoading}>
            <Loader2 className="animate-spin" />
            <p>加载文档中...</p>
          </div>
        ) : previewUrl ? (
          <iframe src={previewUrl} className={styles.previewFrame} />
        ) : (
          <div className={styles.previewError}>
            <FileText size={48} />
            <p>无法加载文档预览</p>
          </div>
        )}
      </div>
    </div>
  ) : (
    // 聊天界面
    <div className={styles.chatContainer}>
      {/* ... 聊天内容 ... */}
    </div>
  )}
</section>
```

---

## 🎨 样式设计

### 预览容器
```css
.previewContainer {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: var(--bg);
}
```

### 预览头部
```css
.previewHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-elev-1);
}
```

### PDF iframe
```css
.previewFrame {
  width: 100%;
  height: 100%;
  border: none;
  background: white;
}
```

### 活动文档高亮
```css
.fileRow.fileRowActive {
  background: rgba(99, 102, 241, 0.1);
  border-color: #6366f1;
}
```

---

## 🧪 使用示例

### 步骤 1: 上传文档
1. 访问知识库详情页
2. 上传一个 PDF 文件
3. 等待文档处理完成（状态变为 `ready`）

### 步骤 2: 预览文档
1. 点击文档列表中的文档
2. 右侧显示 PDF 预览
3. 文档在列表中高亮显示

### 步骤 3: 操作文档
- **收藏**: 点击预览头部的"收藏"按钮
- **关闭**: 点击"关闭预览"按钮返回聊天界面

---

## 🔄 交互流程

```
[文档列表] 
    ↓ 点击文档
[加载中...] 
    ↓ 获取 URL
[显示 PDF 预览]
    ↓ 用户操作
[收藏/关闭]
    ↓ 关闭预览
[返回聊天界面]
```

---

## 📊 API 调用

### 获取文档 URL
```typescript
const response = await kbAPI.getDocumentUrl(kbId, docId);
// 返回: { url: string, name: string }
```

### 收藏文档
```typescript
await favoriteAPI.favoriteDocument(docId, kbId);
```

---

## 🎯 功能优势

### 1. **流畅体验**
- 无需刷新页面
- 快速加载和切换
- 流畅的动画过渡

### 2. **集成收藏**
- 预览时可直接收藏
- 收藏状态实时更新
- 收藏按钮自动切换状态

### 3. **清晰反馈**
- 加载状态提示
- 错误信息友好
- 当前预览文档高亮

### 4. **易用操作**
- 点击文档即可预览
- 关闭按钮位置明显
- 支持键盘快捷键（ESC 关闭，待实现）

---

## 🚀 后续优化建议

### 1. **功能增强**
- [ ] 支持键盘快捷键（ESC 关闭预览）
- [ ] 支持全屏模式
- [ ] 添加页面导航（上一页/下一页）
- [ ] 支持缩放控制

### 2. **性能优化**
- [ ] 预加载下一个文档
- [ ] 缓存已加载的文档
- [ ] 支持大文件分片加载

### 3. **用户体验**
- [ ] 添加预览历史记录
- [ ] 支持双击文档放大
- [ ] 添加打印功能
- [ ] 支持下载原文件

### 4. **多格式支持**
- [ ] 支持图片预览
- [ ] 支持 Word 文档预览
- [ ] 支持 Markdown 渲染
- [ ] 支持文本文件预览

---

## ✅ 测试清单

- [x] 点击文档显示预览
- [x] 加载状态正确显示
- [x] PDF 正确渲染
- [x] 收藏按钮功能正常
- [x] 关闭预览返回聊天
- [x] 当前预览文档高亮
- [x] 错误处理友好
- [x] Toast 提示显示
- [x] 响应式设计适配

---

## 📝 已知问题

### 1. **CORS 问题**
如果 MinIO 或文件服务器的 CORS 配置不正确，可能导致 iframe 加载失败。

**解决方案**: 确保后端返回的 URL 支持跨域访问。

### 2. **某些 PDF 无法预览**
某些加密或特殊格式的 PDF 可能无法在浏览器中直接预览。

**解决方案**: 提供下载选项作为备选方案。

---

## 🎊 总结

PDF 预览功能已完整实现，提供了：

1. ✅ **完整的预览体验** - 点击即可查看
2. ✅ **流畅的交互** - 加载、预览、关闭一气呵成
3. ✅ **集成的收藏** - 预览时可直接收藏
4. ✅ **清晰的状态反馈** - 加载、成功、错误状态明确
5. ✅ **优雅的 UI 设计** - 符合整体风格

用户现在可以在知识库详情页中无缝预览和管理文档！🎉




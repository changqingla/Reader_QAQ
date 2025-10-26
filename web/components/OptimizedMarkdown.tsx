import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import '../styles/markdown.css';

interface OptimizedMarkdownProps {
  children: string;
  className?: string;
}

/**
 * 紧凑型Markdown渲染组件
 * 
 * 设计理念：
 * 1. 不做任何内容预处理，保持Markdown语法完整性
 * 2. 通过自定义组件强制所有元素 margin:0
 * 3. 用CSS选择器精确控制相邻元素间距
 */
export default function OptimizedMarkdown({ children, className }: OptimizedMarkdownProps) {
  return (
    <div className={`markdown-content ${className || ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // 段落：紧凑行高（外边距交给 CSS 控制）
          p: ({ children, ...props }) => (
            <p style={{ lineHeight: 1.4 }} {...props}>
              {children}
            </p>
          ),
          // 标题：强制小边距
          h1: ({ children, ...props }) => (
            <h1 style={{ margin: '4px 0 2px 0', lineHeight: 1.4 }} {...props}>
              {children}
            </h1>
          ),
          h2: ({ children, ...props }) => (
            <h2 style={{ margin: '4px 0 2px 0', lineHeight: 1.4 }} {...props}>
              {children}
            </h2>
          ),
          h3: ({ children, ...props }) => (
            <h3 style={{ margin: '4px 0 2px 0', lineHeight: 1.4 }} {...props}>
              {children}
            </h3>
          ),
          h4: ({ children, ...props }) => (
            <h4 style={{ margin: '4px 0 2px 0', lineHeight: 1.4 }} {...props}>
              {children}
            </h4>
          ),
          h5: ({ children, ...props }) => (
            <h5 style={{ margin: '4px 0 2px 0', lineHeight: 1.4 }} {...props}>
              {children}
            </h5>
          ),
          h6: ({ children, ...props }) => (
            <h6 style={{ margin: '4px 0 2px 0', lineHeight: 1.4 }} {...props}>
              {children}
            </h6>
          ),
          // 列表：仅控制缩进（间距交给 CSS 控制）
          ul: ({ children, ...props }) => (
            <ul style={{ paddingLeft: '24px' }} {...props}>
              {children}
            </ul>
          ),
          ol: ({ children, ...props }) => (
            <ol style={{ paddingLeft: '24px' }} {...props}>
              {children}
            </ol>
          ),
          // 列表项：极小边距，紧凑行高
          li: ({ children, ...props }) => (
            <li style={{ margin: '1px 0', lineHeight: 1.4 }} {...props}>
              {children}
            </li>
          ),
          // 代码块：小边距
          pre: ({ children, ...props }) => (
            <pre style={{ margin: '4px 0' }} {...props}>
              {children}
            </pre>
          ),
          // 引用：小边距
          blockquote: ({ children, ...props }) => (
            <blockquote style={{ margin: '4px 0' }} {...props}>
              {children}
            </blockquote>
          ),
          // 表格：小边距
          table: ({ children, ...props }) => (
            <table style={{ margin: '4px 0' }} {...props}>
              {children}
            </table>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

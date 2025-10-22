import React from 'react';
import { X } from 'lucide-react';
import styles from './CreateKnowledgeModal.module.css';

interface CreateKnowledgeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; description: string; tags: string[] }) => void;
}

export default function CreateKnowledgeModal({ isOpen, onClose, onSubmit }: CreateKnowledgeModalProps) {
  const [name, setName] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [tagsInput, setTagsInput] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      alert('请输入知识库名称');
      return;
    }

    const tags = tagsInput
      .split('/')
      .map(tag => tag.trim())
      .filter(tag => tag.length > 0);

    onSubmit({
      name: name.trim(),
      description: description.trim(),
      tags
    });

    // 重置表单
    setName('');
    setDescription('');
    setTagsInput('');
    onClose();
  };

  const handleClose = () => {
    setName('');
    setDescription('');
    setTagsInput('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={handleClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>新建知识库</h2>
          <button className={styles.closeBtn} onClick={handleClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>
              知识库名称 <span className={styles.required}>*</span>
            </label>
            <input
              type="text"
              className={styles.input}
              placeholder="输入知识库名称"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>概述</label>
            <textarea
              className={styles.textarea}
              placeholder="简单描述这个知识库的用途和内容"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>标签</label>
            <input
              type="text"
              className={styles.input}
              placeholder="用 / 分隔标签，例如：技术/学习/AI"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
            />
            {tagsInput && (
              <div className={styles.tagsPreview}>
                {tagsInput.split('/').map((tag, idx) => {
                  const trimmed = tag.trim();
                  return trimmed ? (
                    <span key={idx} className={styles.tagChip}>
                      {trimmed}
                    </span>
                  ) : null;
                })}
              </div>
            )}
          </div>

          <div className={styles.actions}>
            <button type="button" className={styles.cancelBtn} onClick={handleClose}>
              取消
            </button>
            <button type="submit" className={styles.submitBtn}>
              创建
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}


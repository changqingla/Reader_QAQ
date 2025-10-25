import React from 'react';
import { X } from 'lucide-react';
import { KNOWLEDGE_CATEGORIES, CATEGORY_ICONS } from '@/constants/categories';
import { useToast } from '@/hooks/useToast';
import styles from './CreateKnowledgeModal.module.css';

interface CreateKnowledgeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; description: string; category: string }) => void;
}

export default function CreateKnowledgeModal({ isOpen, onClose, onSubmit }: CreateKnowledgeModalProps) {
  const toast = useToast();
  const [name, setName] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [category, setCategory] = React.useState('其它');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      toast.warning('请输入知识库名称');
      return;
    }

    onSubmit({
      name: name.trim(),
      description: description.trim(),
      category
    });

    // 重置表单
    setName('');
    setDescription('');
    setCategory('其它');
    onClose();
  };

  const handleClose = () => {
    setName('');
    setDescription('');
    setCategory('其它');
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
            <label className={styles.label}>
              分类 <span className={styles.required}>*</span>
            </label>
            <select
              className={styles.select}
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {KNOWLEDGE_CATEGORIES.map((cat) => {
                const Icon = CATEGORY_ICONS[cat];
                return (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                );
              })}
            </select>
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


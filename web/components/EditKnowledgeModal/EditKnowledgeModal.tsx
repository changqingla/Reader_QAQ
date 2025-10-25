/**
 * 编辑知识库模态框组件
 */
import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { KNOWLEDGE_CATEGORIES, CATEGORY_ICONS } from '@/constants/categories';
import styles from './EditKnowledgeModal.module.css';

interface EditKnowledgeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: { name: string; description: string; category: string }) => void;
  initialData: { name: string; description: string; category: string };
}

export default function EditKnowledgeModal({
  isOpen,
  onClose,
  onSave,
  initialData
}: EditKnowledgeModalProps) {
  const [name, setName] = React.useState(initialData.name);
  const [description, setDescription] = React.useState(initialData.description);
  const [category, setCategory] = React.useState(initialData.category || '其它');

  useEffect(() => {
    if (isOpen) {
      setName(initialData.name);
      setDescription(initialData.description);
      setCategory(initialData.category || '其它');
    }
  }, [isOpen, initialData]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      alert('请输入知识库名称');
      return;
    }

    onSave({
      name: name.trim(),
      description: description.trim(),
      category
    });
    onClose();
  };

  const handleClose = () => {
    onClose();
  };

  return (
    <div className={styles.overlay} onClick={handleClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>编辑知识库</h2>
          <button className={styles.closeBtn} onClick={handleClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>知识库名称</label>
            <input
              type="text"
              className={styles.input}
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>概述</label>
            <textarea
              className={styles.textarea}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>分类</label>
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
            <button type="submit" className={styles.saveBtn}>
              保存
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}



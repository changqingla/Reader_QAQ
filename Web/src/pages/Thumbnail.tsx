import React from 'react';
import styles from './Thumbnail.module.css';

const Thumbnail: React.FC = () => {
  return (
    <div className={styles.thumbnail}>
      <div className={styles.imgPage} />
    </div>
  );
};

export default Thumbnail;
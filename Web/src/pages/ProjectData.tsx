import React from 'react';
import styles from './ProjectData.module.css';

const ProjectData: React.FC = () => {
  return (
    <div className={styles.projectData}>
      <div className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <img src="/images/mf6jdh7s-unv8pa1.png" className={styles.logo} alt="Logo" />
          <h2 className={styles.sidebarTitle}>Project Data</h2>
        </div>
        
        <nav className={styles.navigation}>
          <div className={styles.navItem}>
            <img src="/images/mf6jdh7s-unv8pa1.png" className={styles.navIcon} alt="Dashboard" />
            <span>Dashboard</span>
          </div>
          <div className={styles.navItem}>
            <img src="/images/mf6jdh7s-unv8pa1.png" className={styles.navIcon} alt="Projects" />
            <span>Projects</span>
          </div>
          <div className={styles.navItem}>
            <img src="/images/mf6jdh7s-unv8pa1.png" className={styles.navIcon} alt="Analytics" />
            <span>Analytics</span>
          </div>
          <div className={styles.navItem}>
            <img src="/images/mf6jdh7s-unv8pa1.png" className={styles.navIcon} alt="Settings" />
            <span>Settings</span>
          </div>
        </nav>
      </div>
      
      <div className={styles.mainContent}>
        <header className={styles.header}>
          <h1 className={styles.pageTitle}>Project Overview</h1>
          <div className={styles.userProfile}>
            <img src="/images/mf6jdh7s-unv8pa1.png" className={styles.avatar} alt="User Avatar" />
            <span className={styles.userName}>John Doe</span>
          </div>
        </header>
        
        <div className={styles.contentArea}>
          <div className={styles.statsGrid}>
            <div className={styles.statCard}>
              <h3 className={styles.statTitle}>Total Projects</h3>
              <p className={styles.statValue}>24</p>
            </div>
            <div className={styles.statCard}>
              <h3 className={styles.statTitle}>Active Projects</h3>
              <p className={styles.statValue}>12</p>
            </div>
            <div className={styles.statCard}>
              <h3 className={styles.statTitle}>Completed</h3>
              <p className={styles.statValue}>8</p>
            </div>
            <div className={styles.statCard}>
              <h3 className={styles.statTitle}>On Hold</h3>
              <p className={styles.statValue}>4</p>
            </div>
          </div>
          
          <div className={styles.projectList}>
            <h2 className={styles.sectionTitle}>Recent Projects</h2>
            <div className={styles.projectItem}>
              <div className={styles.projectInfo}>
                <h4 className={styles.projectName}>Website Redesign</h4>
                <p className={styles.projectDescription}>Complete overhaul of company website</p>
              </div>
              <div className={styles.projectStatus}>
                <span className={styles.statusBadge}>In Progress</span>
              </div>
            </div>
            <div className={styles.projectItem}>
              <div className={styles.projectInfo}>
                <h4 className={styles.projectName}>Mobile App Development</h4>
                <p className={styles.projectDescription}>iOS and Android app for customer portal</p>
              </div>
              <div className={styles.projectStatus}>
                <span className={styles.statusBadge}>Planning</span>
              </div>
            </div>
            <div className={styles.projectItem}>
              <div className={styles.projectInfo}>
                <h4 className={styles.projectName}>Database Migration</h4>
                <p className={styles.projectDescription}>Migrate legacy database to cloud</p>
              </div>
              <div className={styles.projectStatus}>
                <span className={styles.statusBadge}>Completed</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectData;
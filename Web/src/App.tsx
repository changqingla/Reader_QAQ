import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Thumbnail from './pages/Thumbnail';
import LoginPage from './pages/LoginPage';
import ProjectData from './pages/ProjectData';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navigation">
          <div className="nav-container">
            <h1 className="nav-title">React Pages Demo</h1>
            <div className="nav-links">
              <Link to="/" className="nav-link">Thumbnail</Link>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/project-data" className="nav-link">Project Data</Link>
            </div>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Thumbnail />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/project-data" element={<ProjectData />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

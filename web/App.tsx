import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ToastProvider } from "@/hooks/useToast";
import ProtectedRoute from "@/components/ProtectedRoute";
import Home from "@/pages/Home";
import ChatDetail from "@/pages/ChatDetail";
import Knowledge from "@/pages/Knowledge";
import KnowledgeDetail from "@/pages/KnowledgeDetail";
import Auth from "@/pages/Auth";
import KnowledgeHubDetail from "@/pages/KnowledgeHubDetail";
import PostDetail from "@/pages/PostDetail";
import Favorites from "@/pages/Favorites";
import Notes from "@/pages/Notes";

export default function App() {
  return (
    <ToastProvider>
      <Router>
        <Routes>
          {/* 公开路由 */}
          <Route path="/auth" element={<Auth />} />
          
          {/* 受保护的路由 - 需要登录 */}
          <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/chat/:chatId" element={<ProtectedRoute><ChatDetail /></ProtectedRoute>} />
          <Route path="/knowledge" element={<ProtectedRoute><Knowledge /></ProtectedRoute>} />
          <Route path="/knowledge/:kbId" element={<ProtectedRoute><KnowledgeDetail /></ProtectedRoute>} />
          <Route path="/knowledge/hub/:hubId" element={<ProtectedRoute><KnowledgeHubDetail /></ProtectedRoute>} />
          <Route path="/knowledge/hub/:hubId/post/:postId" element={<ProtectedRoute><PostDetail /></ProtectedRoute>} />
          <Route path="/favorites" element={<ProtectedRoute><Favorites /></ProtectedRoute>} />
          <Route path="/notes" element={<ProtectedRoute><Notes /></ProtectedRoute>} />
          <Route path="/other" element={<ProtectedRoute><div className="text-center text-xl">Other Page - Coming Soon</div></ProtectedRoute>} />
        </Routes>
      </Router>
    </ToastProvider>
  );
}

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
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
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat/:chatId" element={<ChatDetail />} />
        <Route path="/knowledge" element={<Knowledge />} />
        <Route path="/favorites" element={<Favorites />} />
        <Route path="/notes" element={<Notes />} />
        <Route path="/knowledge/:kbId" element={<KnowledgeDetail />} />
        <Route path="/knowledge/hub/:hubId" element={<KnowledgeHubDetail />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/knowledge/hub/:hubId/post/:postId" element={<PostDetail />} />
        <Route path="/other" element={<div className="text-center text-xl">Other Page - Coming Soon</div>} />
      </Routes>
    </Router>
  );
}

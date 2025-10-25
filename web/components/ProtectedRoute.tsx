/**
 * 路由守卫组件
 * 保护需要登录才能访问的路由
 */
import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const token = localStorage.getItem('auth_token');
  
  if (!token) {
    // 未登录，重定向到登录页
    return <Navigate to="/auth" replace />;
  }
  
  // 已登录，渲染子组件
  return <>{children}</>;
}


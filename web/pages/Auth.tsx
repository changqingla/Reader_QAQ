import React from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '@/lib/api';
import styles from './Auth.module.css';

type Tab = 'login' | 'register';

export default function Auth() {
  const navigate = useNavigate();
  const [tab, setTab] = React.useState<Tab>('login');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [name, setName] = React.useState('');
  const [confirm, setConfirm] = React.useState('');
  const [accept, setAccept] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const validateEmail = (v: string) => /.+@.+\..+/.test(v);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      // 前端验证
      if (!validateEmail(email)) {
        setError('请输入有效邮箱');
        return;
      }
      if (password.length < 6) {
        setError('密码至少 6 位');
        return;
      }
      
      if (tab === 'register') {
        if (!name.trim()) {
          setError('请输入昵称');
          return;
        }
        if (password !== confirm) {
          setError('两次密码不一致');
          return;
        }
        
        // 调用注册 API
        const response = await authAPI.register(email, password, name);
        
        // 注册成功后切换到登录页
        setTab('login');
        setPassword('');
        setConfirm('');
        setName('');
        setError('注册成功！请登录');
      } else {
        // 调用登录 API
        const response = await authAPI.login(email, password);
        
        // 保存 token 和用户信息
        localStorage.setItem('auth_token', response.token);
        localStorage.setItem('auth_user', JSON.stringify(response.user));
        localStorage.setItem('userProfile', JSON.stringify({
          name: response.user.name,
          email: response.user.email
        }));
        
        // 跳转到主页
        navigate('/');
      }
    } catch (err: any) {
      setError(err.message || '操作失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.left}>
        <div className={styles.card}>
          <h1 className={styles.title}>你好，欢迎来到Reader！</h1>
          <p className={styles.subtitle}>面向 AI 时代的阅读与知识平台</p>

          <form className={styles.form} onSubmit={handleSubmit}>
            {tab === 'register' && (
              <div className={styles.field}>
                <label className={styles.label}>昵称</label>
                <input className={styles.input} value={name} onChange={e=>setName(e.target.value)} placeholder="给自己起个独具一格的昵称" />
              </div>
            )}
            <div className={styles.field}>
              <label className={styles.label}>邮箱</label>
              <input className={styles.input} value={email} onChange={e=>setEmail(e.target.value)} placeholder="youarebest@example.com" />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>密码</label>
              <input type="password" className={styles.input} value={password} onChange={e=>setPassword(e.target.value)} placeholder="至少 6 位" />
            </div>
            {tab === 'register' && (
              <div className={styles.field}>
                <label className={styles.label}>确认密码</label>
                <input type="password" className={styles.input} value={confirm} onChange={e=>setConfirm(e.target.value)} placeholder="再次输入密码" />
              </div>
            )}

            {/* {tab === 'register' && (
              <label className={styles.hint}>
                <input type="checkbox" checked={accept} onChange={e=>setAccept(e.target.checked)} /> 我已阅读并同意服务协议
              </label>
            )} */}

            {error && <div className={styles.hint} style={{color: error.includes('成功') ? '#22c55e' : '#ef4444'}}>{error}</div>}

            <button className={styles.submit} type="submit" disabled={loading}>
              {loading ? '处理中...' : (tab === 'login' ? '登录' : '注册')}
            </button>
          </form>

          <div className={styles.switchHint}>
            {tab === 'login' ? '还没有账号？' : '已有账号？'}
            <button 
              type="button"
              className={styles.switchBtn} 
              onClick={() => setTab(tab === 'login' ? 'register' : 'login')}
            >
              {tab === 'login' ? '立即注册' : '立即登录'}
            </button>
          </div>
        </div>
      </div>

      <div className={styles.right}>
        <div className={styles.hero}></div>
        <div>
          <div className={styles.caption}>更快进入创造力的涌现区</div>
          <div className={styles.badges}>
            <span className={styles.badge}>即时搜索</span>
            <span className={styles.badge}>文档管理</span>
            <span className={styles.badge}>精准分析</span>
            <span className={styles.badge}>AI 助手</span>
          </div>
        </div>
      </div>
    </div>
  );
}



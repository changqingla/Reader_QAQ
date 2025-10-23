import React from 'react';
import { useNavigate } from 'react-router-dom';
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

  const validateEmail = (v: string) => /.+@.+\..+/.test(v);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!validateEmail(email)) return setError('请输入有效邮箱');
    if (password.length < 6) return setError('密码至少 6 位');
    if (tab === 'register') {
      if (!name.trim()) return setError('请输入昵称');
      if (password !== confirm) return setError('两次密码不一致');
      if (!accept) return setError('请勾选协议');
    }
    // 模拟登录/注册成功，颁发本地 token
    const token = 'local-demo-token.' + Date.now();
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify({ email, name: name || email.split('@')[0] }));
    if (tab === 'register') {
      // 注册成功后跳转到登录页
      setTab('login');
      setPassword('');
      setConfirm('');
      return;
    }
    // 登录成功后跳转到主页
    navigate('/');
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

            {error && <div className={styles.hint} style={{color:'#ef4444'}}>{error}</div>}

            <button className={styles.submit} type="submit">{tab==='login'?'登录':'注册'}</button>
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



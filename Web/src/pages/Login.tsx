import React, { useState } from 'react';
import styles from './Login.module.css';

interface LoginFormData {
  fullName: string;
  email: string;
  password: string;
}

const Login: React.FC = () => {
  const [isLoginMode, setIsLoginMode] = useState(false); // false = 注册模式, true = 登录模式
  const [formData, setFormData] = useState<LoginFormData>({
    fullName: '',
    email: '',
    password: ''
  });
  
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // 模拟API调用
    try {
      if (isLoginMode) {
        console.log('正在登录:', { email: formData.email, password: formData.password });
        // 这里可以添加实际的登录API调用
        await new Promise(resolve => setTimeout(resolve, 1000));
        alert('登录成功！');
      } else {
        console.log('正在创建账户:', formData);
        // 这里可以添加实际的注册API调用
        await new Promise(resolve => setTimeout(resolve, 1000));
        alert('账户创建成功！');
      }
    } catch (error) {
      console.error(isLoginMode ? '登录时出错:' : '创建账户时出错:', error);
      alert(isLoginMode ? '登录失败，请重试。' : '创建账户失败，请重试。');
    } finally {
      setIsLoading(false);
    }
  };





  return (
    <div className={styles.loginPage}>
      <img src="/images/mf6jdhft-nkmk0zp.svg" className={styles.blobsVector} alt="Background decoration" />
      <img src="/images/mf6jdhft-d4m2skj.svg" className={styles.blobsVector2} alt="Background decoration" />
      <img src="/images/mf6jdhft-1g4jr3t.svg" className={styles.blobsVector3} alt="Background decoration" />
      <img src="/images/mf6jdhft-hcnpaov.png" className={styles.mainImage} alt="Main illustration" />
      
      <div className={styles.content}>
        <h1 className={styles.title}>{isLoginMode ? '登录' : '创建您的免费账户'}</h1>
        
        <form onSubmit={handleSubmit} className={styles.form}>
          {!isLoginMode && (
            <div className={styles.fullNameInput}>
              <label className={styles.fullName}>姓名</label>
              <div className={styles.nameInp}>
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  placeholder="请输入您的姓名"
                  className={styles.input}
                  required
                />
              </div>
            </div>
          )}
          
          <div className={styles.emailInput}>
            <label className={styles.fullName}>邮箱</label>
            <div className={styles.emailInp}>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="请输入您的邮箱"
                className={styles.input}
                required
              />
            </div>
          </div>
          
          <div className={styles.passwordInput}>
            <label className={styles.fullName}>密码</label>
            <div className={styles.passwordInp}>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="请输入您的密码"
                className={styles.input}
                required
                minLength={6}
              />
            </div>
          </div>
          
          <button 
            type="submit" 
            className={styles.buttonFrame}
            disabled={isLoading}
          >
            <span className={styles.createAccount}>
              {isLoading 
                ? (isLoginMode ? '正在登录...' : '正在创建账户...') 
                : (isLoginMode ? '登录' : '创建账户')
              }
            </span>
          </button>
        </form>
        
        <p className={styles.alreadyHaveAAccountL4}>
          <span className={styles.alreadyHaveAAccountL}>
            {isLoginMode ? '还没有账户？' : '已有账户？'}
          </span>
          <span className={styles.alreadyHaveAAccountL2}>&nbsp;</span>
          <button 
            type="button" 
            className={styles.loginLink}
            onClick={() => setIsLoginMode(!isLoginMode)}
          >
            <span className={styles.alreadyHaveAAccountL3}>
              {isLoginMode ? '注册' : '登录'}
            </span>
          </button>
        </p>
        


      </div>
    </div>
  );
};

export default Login;
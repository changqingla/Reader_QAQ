import React, { useState } from 'react';
import styles from './LoginPage.module.css';

const LoginPage: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted:', { fullName, email, password });
  };

  return (
    <div className={styles.loginPage}>
      <img src="/images/mf6jdhft-nkmk0zp.svg" className={styles.blobsVector} alt="Background blob" />
      <img src="/images/mf6jdhft-d4m2skj.svg" className={styles.blobsVector2} alt="Background blob" />
      <img src="/images/mf6jdhft-1g4jr3t.svg" className={styles.blobsVector3} alt="Background blob" />
      <img src="/images/mf6jdhft-hcnpaov.png" className={styles.mainImage} alt="Hot air balloon" />
      
      <div className={styles.content}>
        <p className={styles.title}>Create your Free Account</p>
        
        <form onSubmit={handleSubmit}>
          <div className={styles.fullNameInput}>
            <p className={styles.fullName}>Full Name</p>
            <div className={styles.nameInp}>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your Full Name here"
                className={styles.input}
              />
            </div>
          </div>
          
          <div className={styles.emailInput}>
            <p className={styles.fullName}>Email</p>
            <div className={styles.emailInp}>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your Email here"
                className={styles.input}
              />
            </div>
          </div>
          
          <div className={styles.passwordInput}>
            <p className={styles.fullName}>Password</p>
            <div className={styles.passwordInp}>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your Password here"
                className={styles.input}
              />
            </div>
          </div>
          
          <button type="submit" className={styles.buttonFrame}>
            <p className={styles.createAccount}>Create Account</p>
          </button>
        </form>
        
        <p className={styles.alreadyHaveAAccountL4}>
          <span className={styles.alreadyHaveAAccountL}>Already have a account?</span>
          <span className={styles.alreadyHaveAAccountL2}>&nbsp;</span>
          <span className={styles.alreadyHaveAAccountL3}>Log in</span>
        </p>
        
        <p className={styles.aOr}>- OR -</p>
        
        <div className={styles.autoWrapper}>
          <button className={styles.buttonFrame2}>
            <img src="/images/mf6jdhfu-tibvv6d.png" className={styles.google} alt="Google" />
            <p className={styles.singUpWithGoogle}>Sign up with Google</p>
          </button>
          
          <button className={styles.buttonFrame3}>
            <img src="/images/mf6jdhft-8qkmhsf.png" className={styles.google} alt="GitHub" />
            <p className={styles.singUpWithGitHub}>Sign up with GitHub</p>
          </button>
        </div>
        
        <p className={styles.reservedDirectsToLeo}>Reserved directs to Leo Barreto</p>
      </div>
    </div>
  );
};

export default LoginPage;
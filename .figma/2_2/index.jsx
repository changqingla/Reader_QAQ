import React from 'react';

import styles from './index.module.scss';

const Component = () => {
  return (
    <div className={styles.loginPage}>
      <img src="../image/mf6jdhft-nkmk0zp.svg" className={styles.blobsVector} />
      <img src="../image/mf6jdhft-d4m2skj.svg" className={styles.blobsVector2} />
      <img src="../image/mf6jdhft-1g4jr3t.svg" className={styles.blobsVector3} />
      <img src="../image/mf6jdhft-hcnpaov.png" className={styles.mainImage} />
      <div className={styles.content}>
        <p className={styles.title}>Create your Free Account</p>
        <div className={styles.fullNameInput}>
          <p className={styles.fullName}>Full Name</p>
          <div className={styles.nameInp}>
            <p className={styles.enterYourFulllNameHe}>
              Enter your Fulll Name here
            </p>
            <div className={styles.input} />
          </div>
        </div>
        <div className={styles.emailInput}>
          <p className={styles.fullName}>Email</p>
          <div className={styles.emailInp}>
            <p className={styles.enterYourEmailHere}>Enter your Email here</p>
            <div className={styles.input} />
          </div>
        </div>
        <div className={styles.passwordInput}>
          <p className={styles.fullName}>Password</p>
          <div className={styles.passwordInp}>
            <p className={styles.enterYourPasswordHer}>Enter your Password here</p>
            <div className={styles.input} />
          </div>
        </div>
        <div className={styles.buttonFrame}>
          <p className={styles.createAccount}>Create Account</p>
        </div>
        <p className={styles.alreadyHaveAAccountL4}>
          <span className={styles.alreadyHaveAAccountL}>
            Already have a account?
          </span>
          <span className={styles.alreadyHaveAAccountL2}>&nbsp;</span>
          <span className={styles.alreadyHaveAAccountL3}>Log in</span>
        </p>
        <p className={styles.aOr}>- OR -</p>
        <div className={styles.autoWrapper}>
          <div className={styles.buttonFrame2}>
            <img src="../image/mf6jdhfu-tibvv6d.png" className={styles.google} />
            <p className={styles.singUpWithGoogle}>Sing up with Google</p>
          </div>
          <div className={styles.buttonFrame3}>
            <img src="../image/mf6jdhft-8qkmhsf.png" className={styles.google} />
            <p className={styles.singUpWithGitHub}>Sing up with GitHub</p>
          </div>
        </div>
        <p className={styles.reservedDirectsToLeo}>
          Reserved directs to Leo Barreto
        </p>
      </div>
    </div>
  );
}

export default Component;

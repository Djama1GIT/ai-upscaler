import React from 'react';
import { Result, Button } from 'antd';
import { NavigateFunction, useNavigate } from 'react-router-dom';
import styles from './PageNotFound.module.scss';

const PageNotFound: React.FC = () => {
  const navigate: NavigateFunction = useNavigate();

  const handleNavigateToHome = (): void => {
    navigate('/');
  };

  return (
    <div className={styles.page}>
      <Result
        status={"error"}
        title="404"
        subTitle="Извините, страница, которую вы посетили, не существует."
        extra={
          <Button type="primary" onClick={handleNavigateToHome}>
            На главную
          </Button>
        }
      />
    </div>
  );
};

export default React.memo(PageNotFound);
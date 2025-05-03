import React  from 'react';
import { Layout, App } from 'antd';
import styles from './Home.module.scss';

import Header from "./Header/Header";
import Content from "./Content/Content";
import Footer from "./Footer/Footer";

const Homepage: React.FC = () => {
  return (
    <App>
      <Layout className={styles.layout}>
        <Header />
        <Content />
        <Footer />
      </Layout>
    </App>
  );
};

export default React.memo(Homepage);
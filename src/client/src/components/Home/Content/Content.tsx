import React from 'react';
import styles from './Content.module.scss';

import { Layout } from "antd";

import Title from "./Title/Title";
import UploadAndProcess from "./UploadAndProcess/UploadAndProcess";
import Features from "./Features/Features";

const { Content } = Layout;

const ContentComponent: React.FC = () => {
  return (
    <Content className={styles.content}>
      <Title />
      <UploadAndProcess />
      <Features />
    </Content>
  );
};

export default React.memo(ContentComponent);
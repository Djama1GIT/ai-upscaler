import React from 'react';
import { Card, Row, Col, Typography } from 'antd';
import { UploadOutlined, RocketOutlined, UpOutlined } from '@ant-design/icons';
import styles from './Features.module.scss';

const { Title, Text } = Typography;

const Features: React.FC = () => {
  return (
    <Row gutter={[24, 24]} className={styles.featuresRow}>
      <Col xs={24} md={12} lg={8}>
        <Card hoverable className={styles.featureCard}>
          <div className={styles.featureIcon}>
            <UpOutlined />
          </div>
          <Title level={4} className={styles.featureTitle}>Высокое качество</Title>
          <Text>
            Наш алгоритм обработки изображений увеличивает качество фотографий и улучшает их детализацию
          </Text>
        </Card>
      </Col>
      <Col xs={24} md={12} lg={8}>
        <Card hoverable className={styles.featureCard}>
          <div className={styles.featureIcon}>
            <RocketOutlined />
          </div>
          <Title level={4} className={styles.featureTitle}>Быстрая обработка</Title>
          <Text>
            Высокая скорость обработки благодаря новейшим технологиям
          </Text>
        </Card>
      </Col>
      <Col xs={24} md={12} lg={8}>
        <Card hoverable className={styles.featureCard}>
          <div className={styles.featureIcon}>
            <UploadOutlined />
          </div>
          <Title level={4} className={styles.featureTitle}>Множество форматов</Title>
          <Text>
            Обрабатывайте фотографии любых удобных для вас форматов: PNG, JPG и многие другие
          </Text>
        </Card>
      </Col>
    </Row>
  );
};

export default React.memo(Features);
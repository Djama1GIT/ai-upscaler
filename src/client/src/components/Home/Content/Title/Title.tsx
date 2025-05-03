import React from "react";
import { Col, Row, Typography } from "antd";
import styles from "./Title.module.scss";

const { Title, Text } = Typography;

const TitleComponent: React.FC = () => {
  return (
    <Row justify="center" className={styles.titleRow}>
      <Col xs={24} md={18} lg={16}>
        <Title level={2} className={styles.mainTitle}>
          Улучшите качество ваших фотографий с помощью искусственного интеллекта!
        </Title>
        <Text type="secondary" className={styles.subtitle}>
          Загрузите изображение, и наш AI увеличит его разрешение без потери качества.
          Поддерживаемые форматы: JPG, PNG, WEBP.
        </Text>
      </Col>
    </Row>
  );
};

export default React.memo(TitleComponent);
import React, { useState } from 'react';
import { Button, Typography, Layout, Switch, Modal, Table, Space, Spin, Alert, Card, Row, Col } from 'antd';
import { QuestionCircleOutlined, HistoryOutlined, DownloadOutlined } from '@ant-design/icons';
import styles from './Header.module.scss';
import HowItWorksModal from "./HowItWorksModal/HowItWorksModal";
import { useUpscalerStore } from "../../../store";

const { Header } = Layout;
const { Title, Text } = Typography;

interface ModelUsage {
  [model: string]: {
    [version: string]: number;
  };
}

interface AvgMetrics {
  [key: string]: number;
}

interface ScaleFactors {
  [factor: string]: number;
}

interface StatisticsData {
  model_usage: ModelUsage;
  avg_processing_time: AvgMetrics;
  avg_file_size: AvgMetrics;
  success_rate: number;
  scale_factors: ScaleFactors;
}

const HeaderComponent: React.FC = () => {
  const theme = useUpscalerStore(state => state.theme);
  const setTheme = useUpscalerStore(state => state.setTheme);
  const isDarkMode = theme === 'dark';

  const setAboutModalVisible = useUpscalerStore(state => state.setAboutModalVisible);
  const [historyModalVisible, setHistoryModalVisible] = useState(false);
  const [statistics, setStatistics] = useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleThemeChange = (checked: boolean): void => {
    setTheme(checked ? 'dark' : 'light');
  };

  const showAboutModal = (): void => {
    setAboutModalVisible(true);
  };

  const showHistoryModal = async (): Promise<void> => {
    setHistoryModalVisible(true);
    setLoading(true);
    setError(null);

    try {
      // @ts-ignore
      const response = await fetch(`${window.CONSTS.HOST}/api/latest/history/statistics`);
      if (!response.ok) {
        throw new Error('Failed to fetch statistics');
      }
      const data = await response.json();
      setStatistics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = (): void => {
    // @ts-ignore
    window.open(`${window.CONSTS.HOST}/api/latest/history/report`, '_blank');
  };

  const renderModelUsageTable = () => {
    if (!statistics?.model_usage) return null;

    const dataSource = Object.entries(statistics.model_usage).flatMap(([model, versions]) =>
      Object.entries(versions).map(([version, count]) => ({
        model,
        version,
        count
      }))
    );

    return (
      <Card title="Использование моделей" size="small" style={{ marginBottom: 16 }}>
        <Table
          columns={[
            { title: 'Модель', dataIndex: 'model', key: 'model' },
            { title: 'Версия', dataIndex: 'version', key: 'version' },
            {
              title: 'Количество',
              dataIndex: 'count',
              key: 'count',
              render: (value) => <Text strong>{value.toFixed(0)}%</Text>
            }
          ]}
          dataSource={dataSource}
          pagination={false}
          size="small"
          bordered
        />
      </Card>
    );
  };

  const renderMetricsTable = () => {
    if (!statistics?.avg_processing_time || !statistics?.avg_file_size) return null;

    const dataSource = Object.keys(statistics.avg_processing_time).map(key => ({
      key,
      processing_time: statistics.avg_processing_time[key],
      file_size: statistics.avg_file_size[key]
    }));

    return (
      <Card title="Средние показатели" size="small" style={{ marginBottom: 16 }}>
        <Table
          columns={[
            { title: 'Модель', dataIndex: 'key', key: 'key' },
            {
              title: 'Среднее время обработки (сек)',
              dataIndex: 'processing_time',
              key: 'processing_time',
              render: (value) => value.toFixed(2)
            },
            {
              title: 'Средний размер файла (KB)',
              dataIndex: 'file_size',
              key: 'file_size',
              render: (value) => (value / 1024).toFixed(2)
            }
          ]}
          dataSource={dataSource}
          pagination={false}
          size="small"
          bordered
        />
      </Card>
    );
  };

  const renderScaleFactorsTable = () => {
    if (!statistics?.scale_factors) return null;

    const dataSource = Object.entries(statistics.scale_factors).map(([factor, count]) => ({
      factor,
      count
    }));

    return (
      <Card title="Коэффициенты масштабирования" size="small" style={{ marginBottom: 16 }}>
        <Table
          columns={[
            { title: 'Коэффициент', dataIndex: 'factor', key: 'factor' },
            {
              title: 'Количество',
              dataIndex: 'count',
              key: 'count',
              render: (value) => <Text strong>{value.toFixed(0)}%</Text>
            }
          ]}
          dataSource={dataSource}
          pagination={false}
          size="small"
          bordered
        />
      </Card>
    );
  };

  const renderSuccessRateCard = () => {
    if (!statistics?.success_rate) return null;

    return (
      <Card title="Успешность операций" size="small" style={{ marginBottom: 16 }}>
        <Row align="middle" gutter={16}>
          <Col>
            <Text style={{ fontSize: 24 }}>{statistics.success_rate}%</Text>
          </Col>
          <Col>
            {statistics.success_rate === 100 ? (
              <Text type="success">Все операции успешны</Text>
            ) : statistics.success_rate > 90 ? (
              <Text type="warning">Высокий процент успеха</Text>
            ) : (
              <Text type="danger">Низкий процент успеха</Text>
            )}
          </Col>
        </Row>
      </Card>
    );
  };

  return (
    <div>
      <Header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logoContainer}>
            <Title level={3} className={styles.title}>
              <span className={styles.logoText}>AI</span>
              <span className={styles.logoHighlight}>Upscaler</span>
            </Title>
            <Text type="secondary" className={styles.tagline}>
              AI-powered Image Upscaler
            </Text>
          </div>

          <Space>
            <Button
              type="text"
              icon={<HistoryOutlined />}
              className={styles.historyButton}
              onClick={showHistoryModal}
            >
              История
            </Button>
            <Button
              type="text"
              icon={<QuestionCircleOutlined/>}
              className={styles.howItWorksButton}
              onClick={showAboutModal}
            >
              Как это работает
            </Button>
            <Switch
              checkedChildren="Темная"
              unCheckedChildren="Светлая"
              checked={isDarkMode}
              className={styles.themeToggle}
              onChange={handleThemeChange}
              title="Сменить цветовую схему"
            />
          </Space>
        </div>
      </Header>

      <HowItWorksModal />

      <Modal
        title="Статистика использования"
        open={historyModalVisible}
        onCancel={() => setHistoryModalVisible(false)}
        footer={[
          <Button
            key="download"
            type="primary"
            icon={<DownloadOutlined />}
            onClick={downloadReport}
          >
            Скачать отчет по истории запросов
          </Button>,
          <Button key="close" onClick={() => setHistoryModalVisible(false)}>
            Закрыть
          </Button>,
        ]}
        width={900}
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: '24px' }}>
            <Spin size="large" />
          </div>
        ) : error ? (
          <Alert message="Ошибка" description={error} type="error" showIcon />
        ) : statistics ? (
          <div>
            {renderSuccessRateCard()}
            {renderModelUsageTable()}
            {renderMetricsTable()}
            {renderScaleFactorsTable()}
          </div>
        ) : null}
      </Modal>
    </div>
  );
};

export default React.memo(HeaderComponent);
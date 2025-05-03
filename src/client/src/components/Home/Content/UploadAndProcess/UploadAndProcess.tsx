import React, { useState, useEffect, useRef } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Progress,
  Row,
  Space,
  Typography,
  Upload,
  UploadProps,
  message,
  Image,
  Select
} from "antd";
import { DownloadOutlined, UploadOutlined } from "@ant-design/icons";
import styles from "./UploadAndProcess.module.scss";

import { useUpscalerStore } from "../../../../store";

const { Text, Title } = Typography;
const { Option } = Select;

const UploadAndProcessComponent: React.FC = () => {
  const fileList = useUpscalerStore(state => state.fileList);
  const isUploading = useUpscalerStore(state => state.isUploading);
  const isProcessing = useUpscalerStore(state => state.isProcessing);
  const progress = useUpscalerStore(state => state.progress);
  const setFileList = useUpscalerStore(state => state.setFileList);
  const setIsUploading = useUpscalerStore(state => state.setIsUploading);
  const setIsProcessing = useUpscalerStore(state => state.setIsProcessing);
  const setProgress = useUpscalerStore(state => state.setProgress);

  const [resultImage, setResultImage] = useState<string | null>(null);
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processingTime, setProcessingTime] = useState<number>(0);
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("EDSR_x2");

  const processingStartTime = useRef<number>(0);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Очищаем интервал при размонтировании компонента
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        // @ts-ignore
        const response = await fetch(`${window.CONSTS.HOST}/api/latest/models/`);
        if (!response.ok) throw new Error("Ошибка загрузки моделей");
        const data = await response.json();
        setModels(data.models);
        if (data.models.length > 0) {
          setSelectedModel(data.models[0]);
        }
      } catch (error) {
        console.error("Failed to fetch models:", error);
        message.error("Не удалось загрузить список моделей");
      }
    };

    fetchModels();
  }, []);

  useEffect(() => {
    setResultImage(null);
  }, [selectedModel]);

  const handleUpload: UploadProps['onChange'] = (info) => {
    let newFileList = [...info.fileList];
    newFileList = newFileList.slice(-1);

    if (newFileList.length > 0) {
      const file = newFileList[0];
      if (file.originFileObj) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setOriginalImage(e.target?.result as string);
        };
        reader.readAsDataURL(file.originFileObj);
      }
    }

    setFileList(newFileList);
    setError(null);
    setResultImage(null);
  };

  const startProcessing = async (): Promise<void> => {
    if (fileList.length === 0) return;

    // Очищаем предыдущий интервал, если он существует
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }

    const file = fileList[0];
    if (!file.originFileObj) return;

    setIsUploading(true);
    setIsProcessing(true);
    setResultImage(null);
    setProgress(10);
    setError(null);
    processingStartTime.current = Date.now();

    // Симуляция прогресса
    progressIntervalRef.current = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 25) {
          setIsUploading(false);
        }
        if (prev >= 98) {
          return 98;
        }
        if (prev < 20) return prev + 1;
        if (prev >= 70) return prev + 0.1;
        if (prev >= 90) return prev + 0.05;
        else return prev + 0.5;
      });
    }, 100);

    try {
      const formData = new FormData();
      formData.append('image', file.originFileObj);
      formData.append('model', selectedModel);

      // @ts-ignore
      const response = await fetch(`${window.CONSTS.HOST}/api/latest/upscaler/upscale/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Ошибка сервера: ${response.status}`);
      }

      const blob = await response.blob();
      const reader = new FileReader();
      reader.onload = () => {
        setResultImage(reader.result as string);
        setProcessingTime(Math.round((Date.now() - processingStartTime.current) / 1000));
        setProgress(100);
      };
      reader.readAsDataURL(blob);

    } catch (error) {
      handleError(error instanceof Error ? error.message : String(error));
    } finally {
      setIsUploading(false);
      setIsProcessing(false);
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
    }
  };

  const handleError = (error: string) => {
    console.error('Processing error:', error);
    setError(error);
    setIsUploading(false);
    setIsProcessing(false);
    setProgress(0);
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
    message.error(`Ошибка обработки: ${error}`);
  };

  const downloadResult = (): void => {
    if (!resultImage) return;

    const link = document.createElement('a');
    link.href = resultImage;
    link.download = `upscaled_${fileList[0]?.name || 'image.png'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const uploadProps: UploadProps = {
    name: "image",
    multiple: false,
    accept: "image/*",
    fileList,
    onChange: handleUpload,
    beforeUpload: () => false,
    className: styles.dragger,
    disabled: isUploading || isProcessing,
    onRemove: () => {
      setResultImage(null);
      setOriginalImage(null);
      setProgress(0);
      setError(null);
    }
  };

  const progressStrokeColor = {
    '0%': '#108ee9',
    '100%': '#87d068',
  };

  return (
    <Row justify="center" className={styles.rowContainer}>
      <Col xs={24} md={18} lg={12}>
        <Card hoverable className={styles.uploadCard}>
          <Upload.Dragger {...uploadProps}>
            <UploadOutlined className={styles.uploadIcon}/>
            <Title level={4} className={styles.uploadTitle}>Перетащите изображение сюда</Title>
            <Text type="secondary">или нажмите для выбора файла</Text>
            <div className={styles.fileTypes}>
              <Text type="secondary">JPG, PNG, WEBP</Text>
            </div>
          </Upload.Dragger>

          <Divider />

          <Space direction="vertical" className={styles.bottomSpace} style={{ width: '100%' }}>
            <div className={styles.modelSelection}>
              <Text strong style={{ marginRight: 8 }}>Модель:</Text>
              <Select
                value={selectedModel}
                onChange={setSelectedModel}
                disabled={isUploading || isProcessing}
                style={{ width: 200 }}
              >
                {models.map(model => (
                  <Option key={model} value={model}>
                    {model}
                  </Option>
                ))}
              </Select>
            </div>

            <Button
              type="primary"
              size="large"
              block
              onClick={startProcessing}
              disabled={fileList.length === 0 || isUploading || isProcessing}
              loading={isUploading || isProcessing}
              className={styles.processButton}
            >
              {isUploading ? 'Загрузка файла...' :
                isProcessing ? 'Улучшение изображения...' : 'Улучшить изображение'}
            </Button>

            {error && (
              <Alert
                message="Ошибка обработки"
                description={error}
                type="error"
                showIcon
                closable
                onClose={() => setError(null)}
                className={styles.errorAlert}
              />
            )}

            {(isUploading || isProcessing) && (
              <div className={styles.progressContainer}>
                <Text strong>
                  {isUploading ? 'Загрузка изображения на сервер...' : 'Улучшение изображения...'}
                </Text>
                <Progress
                  percent={Number(progress.toFixed(0))}
                  status="active"
                  strokeColor={progressStrokeColor}
                />
                <Text type="secondary" className={styles.progressTip}>
                  {isUploading ? 'Пожалуйста, подождите...' :
                    'Обычно обработка занимает 30-50 секунд в зависимости от размера изображения'}
                </Text>
              </div>
            )}

            {originalImage && resultImage && (
              <div className={styles.comparisonContainer}>
                <Title level={5} className={styles.comparisonTitle}>
                  Результат улучшения ({selectedModel})
                </Title>
                <div className={styles.imagesComparison}>
                  <div className={styles.imagePair}>
                    <div className={styles.imageWrapper}>
                      <Text strong className={styles.imageLabel}>Оригинал</Text>
                      <Image
                        src={originalImage}
                        alt="Original"
                        rootClassName={styles.comparisonImage}
                      />
                    </div>
                    <div className={styles.imageWrapper}>
                      <Text strong className={styles.imageLabel}>Улучшенное</Text>
                      <Image
                        src={resultImage}
                        alt="Upscaled"
                        rootClassName={styles.comparisonImage}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {progress === 100 && resultImage && (
              <Alert
                message={
                  <Space>
                    <span>Обработка завершена!</span>
                    <Text type="success">Готово за {processingTime} сек</Text>
                  </Space>
                }
                type="success"
                showIcon
                action={
                  <Button
                    type="primary"
                    icon={<DownloadOutlined/>}
                    onClick={downloadResult}
                  >
                    Скачать
                  </Button>
                }
                className={styles.resultAlert}
              />
            )}
          </Space>
        </Card>
      </Col>
    </Row>
  );
};

export default React.memo(UploadAndProcessComponent);
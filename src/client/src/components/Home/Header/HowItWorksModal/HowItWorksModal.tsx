import { QuestionCircleOutlined } from "@ant-design/icons";
import { Button, Modal, Typography } from "antd";
import React from "react";
import { useUpscalerStore } from "../../../../store";

const { Title, Paragraph } = Typography;

const HowItWorksModal: React.FC = () => {
  const aboutModalVisible = useUpscalerStore(state => state.aboutModalVisible);
  const setAboutModalVisible = useUpscalerStore(state => state.setAboutModalVisible);

  const handleCancel = (): void => {
    setAboutModalVisible(false);
  };

  const modalTitle: React.ReactNode = (
    <div>
      <QuestionCircleOutlined/>
      <span> Как это работает</span>
    </div>
  );

  const modalFooter: React.ReactNode[] = [
    <Button key="close" onClick={handleCancel}>
      Закрыть
    </Button>
  ];

  return (
    <Modal
      title={modalTitle}
      open={aboutModalVisible}
      onCancel={handleCancel}
      footer={modalFooter}
      width={800}
    >
      <Title level={4}>Технология EDSR (Enhanced Deep Super-Resolution)</Title>
      <Paragraph>
        Наш сервис использует передовую технологию EDSR, основанную на глубоких нейронных сетях,
        для улучшения качества и увеличения разрешения изображений.
      </Paragraph>

      <Title level={5}>Основные возможности:</Title>
      <ul>
        <li>Увеличение разрешения изображений в 2x, 3x и 4x без потери качества</li>
        <li>Улучшение детализации и четкости изображений</li>
        <li>Уменьшение шумов и артефактов сжатия</li>
        <li>Сохранение естественных текстур и границ</li>
      </ul>

      <Title level={5}>Как это работает технически:</Title>
      <Paragraph>
        EDSR использует глубокую сверточную нейронную сеть с остаточными блоками,
        специально оптимизированную для задачи супер-разрешения. Модель обучается
        на парах изображений низкого и высокого качества, изучая сложные взаимосвязи
        для точного восстановления деталей.
      </Paragraph>

      <Paragraph>
        В отличие от традиционных методов апскейлинга, EDSR не просто интерполирует пиксели,
        а генерирует новые, более точные детали на основе обученных паттернов.
      </Paragraph>
    </Modal>
  );
};

export default React.memo(HowItWorksModal);
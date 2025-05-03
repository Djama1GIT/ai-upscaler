import { create } from 'zustand';
import { UploadFile } from "antd";

type Theme = 'dark' | 'light';

interface UpscalerStoreState {
  theme: Theme;
  aboutModalVisible: boolean;

  fileList: UploadFile[];
  isUploading: boolean;
  isProcessing: boolean;
  progress: number;

  setTheme: (theme: Theme) => void;
  setAboutModalVisible: (visible: boolean) => void;

  setFileList: (fileList: UploadFile[]) => void;
  setIsUploading: (uploading: boolean) => void;
  setIsProcessing: (isProcessing: boolean) => void;
  setProgress: (progress: number | ((prev: number) => number)) => void;
}

export const useUpscalerStore = create<UpscalerStoreState>((set) => ({
  theme: (window.localStorage.getItem('theme') as Theme) || 'dark',
  aboutModalVisible: false,

  fileList: [],
  isUploading: false,
  isProcessing: false,
  progress: 0,

  setTheme: (theme: Theme) => {
    set({ theme });
    window.localStorage.setItem('theme', theme);
  },
  setAboutModalVisible: (visible: boolean) => set({ aboutModalVisible: visible }),

  setFileList: (fileList: UploadFile[]) => set({ fileList }),
  setIsUploading: (isUploading: boolean) => set({ isUploading }),
  setIsProcessing: (isProcessing: boolean) => set({ isProcessing }),
  setProgress: (progress: number | ((prev: number) => number)) =>
    set(state => ({
      progress: typeof progress === 'function' ? progress(state.progress) : progress,
    })),
}));
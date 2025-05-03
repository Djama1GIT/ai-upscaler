import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { router } from "./routes";
import { ConfigProvider, theme } from "antd";
import './App.css';

import { useUpscalerStore } from "./store";

const App: React.FC = () => {
  const appTheme = useUpscalerStore(state => state.theme);
  const isDarkMode = appTheme === 'dark';

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', appTheme);
  }, [appTheme]);

  return (
    <BrowserRouter>
      <ConfigProvider
        theme={{
          algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
          components: {
            Layout: {
              colorBgHeader: isDarkMode ? "#111" : "#fff",
              colorBgBody: isDarkMode ? "#000" : "#f7f7f7",
              colorBgLayout: isDarkMode ? "#111" : "#fff",
            },
          },
          cssVar: true,
          hashed: false,
        }}
      >
        <div className="App">
          <Routes>
            {router.map((route) => (
              <Route key={route.path} path={route.path} element={route.element}/>
            ))}
          </Routes>
        </div>
      </ConfigProvider>
    </BrowserRouter>
  );
}

export default React.memo(App);
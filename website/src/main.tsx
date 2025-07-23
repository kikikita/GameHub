import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import App from './App.tsx';
import './index.css';
import PrivacyPolicy from './pages/PrivacyPolicy.tsx';
import DataProcessing from './pages/DataProcessing.tsx';
import Layout from './components/Layout.tsx';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<App />} />
          <Route path="privacy-policy" element={<PrivacyPolicy />} />
          <Route path="data-processing" element={<DataProcessing />} />
        </Route>
      </Routes>
    </Router>
  </React.StrictMode>,
);

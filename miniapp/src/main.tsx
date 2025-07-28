import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n';
import App from './App.tsx'
import { initTg } from './telegram/init.ts'
import { initBackButton } from './telegram/backButton.ts'

initTg();
initBackButton();

if (window.location.hostname !== 'localhost') {
  import('@sentry/react').then(({ init }) => {
    init({
      dsn: "https://4ef13e54b9f2926e33d4a30ac195c76a@o4509747860865024.ingest.de.sentry.io/4509747862241360",
    });
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
import { useState } from 'react';
import './Footer.css';
import { smoothScrollToTop } from '../utils/smoothScroll';

function Footer() {
  const [showTooltip, setShowTooltip] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setShowTooltip(true);
      setTimeout(() => {
        setShowTooltip(false);
      }, 2000); // Hide tooltip after 2 seconds
    });
  };

  return (
    <footer className="footer" id="contact">
      <div className="footer-content">
        <span className="copyright-text">Copyright {new Date().getFullYear()} Immersia</span>
        <div className="email-container">
          <span className="email-text" onClick={() => copyToClipboard('contact@immersia.fun')}>
            contact@immersia.fun
          </span>
          {showTooltip && <div className="tooltip">Copied to clipboard!</div>}
        </div>
        <button onClick={() => smoothScrollToTop()} className="back-to-top">
          Back to top ↑
        </button>
      </div>
    </footer>
  );
}

export default Footer; 
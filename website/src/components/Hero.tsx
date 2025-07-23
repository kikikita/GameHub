import React from 'react';
import './Hero.css';
import { smoothScrollTo } from '../utils/smoothScroll';
import mainSplash from '../assets/images/main-splash.png';

function Hero() {
  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, targetId: string) => {
    e.preventDefault();
    smoothScrollTo(targetId);
  };

  return (
    <div className="hero" style={{ backgroundImage: `url(${mainSplash})` }}>
      <div className="hero-content">
        <h1>Unleash your story</h1>
        <p>
          Create and play in unique worlds born from artificial intelligence. Turn your boldest ideas into captivating
          visual novels. Subscribe for updates to stay informed.
        </p>
        <a href="#subscribe" className="subscribe-button" onClick={(e) => handleNavClick(e, 'subscribe')}>
          Subscribe for updates
        </a>
      </div>
    </div>
  );
}

export default Hero; 
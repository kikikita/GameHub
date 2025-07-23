import React from 'react';
import './Header.css';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { smoothScrollTo } from '../utils/smoothScroll';

function Header() {
  const location = useLocation();
  const navigate = useNavigate();

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, targetId: string) => {
    e.preventDefault();
    if (location.pathname === '/') {
      smoothScrollTo(targetId);
    } else {
      navigate(`/#${targetId}`);
    }
  };

  return (
    <header className="header">
      <div className="header-left">
        <a href="#roadmap" onClick={(e) => handleNavClick(e, 'roadmap')}>
          Roadmap
        </a>
        <a href="#gallery" onClick={(e) => handleNavClick(e, 'gallery')}>
          Gallery
        </a>
      </div>
      <div className="header-center">
        <Link to="/" className="home-link">
          Immersia
        </Link>
      </div>
      <div className="header-right">
        <a href="#contact" onClick={(e) => handleNavClick(e, 'contact')}>
          Contact
        </a>
      </div>
    </header>
  );
}

export default Header; 
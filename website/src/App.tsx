import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import './App.css';
import Hero from './components/Hero';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import Roadmap from './components/Roadmap';
import Subscribe from './components/Subscribe';
import Gallery from './components/Gallery';
import { smoothScrollTo } from './utils/smoothScroll';

function App() {
  const location = useLocation();

  useEffect(() => {
    if (location.hash) {
      setTimeout(() => {
        smoothScrollTo(location.hash.substring(1));
      }, 100);
    }
  }, [location]);

  return (
    <>
      <Hero />
      <Features />
      <HowItWorks />
      <Roadmap />
      <Subscribe />
      <Gallery />
    </>
  );
}

export default App; 
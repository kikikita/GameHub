import { useState, useEffect } from 'react';
import './Gallery.css';
import Lightbox from './Lightbox';

import gallery1 from '../assets/images/gallery-1.jpg';
import gallery2 from '../assets/images/gallery-2.jpg';
import gallery3 from '../assets/images/gallery-3.jpg';
import gallery4 from '../assets/images/gallery-4.jpg';

const images = [gallery1, gallery2, gallery3, gallery4];

function Gallery() {
  const [selectedImage, setSelectedImage] = useState<number | null>(null);

  const openLightbox = (index: number) => {
    setSelectedImage(index);
  };

  const closeLightbox = () => {
    setSelectedImage(null);
  };

  const showPrev = () => {
    if (selectedImage !== null) {
      setSelectedImage((selectedImage - 1 + images.length) % images.length);
    }
  };

  const showNext = () => {
    if (selectedImage !== null) {
      setSelectedImage((selectedImage + 1) % images.length);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeLightbox();
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return (
    <section className="gallery" id="gallery">
      <h2>Explore worlds</h2>
      <p className="gallery-description">
        See the potential of Immersia firsthand. Browse our gallery of AI-generated worlds and visual novel
        elements for inspiration.
      </p>
      <div className="gallery-grid">
        {images.map((image, index) => (
          <div className="gallery-item" key={index} onClick={() => openLightbox(index)}>
            <img src={image} alt={`Gallery image ${index + 1}`} />
          </div>
        ))}
      </div>
      {selectedImage !== null && (
        <Lightbox
          src={images[selectedImage]}
          onClose={closeLightbox}
          onPrev={showPrev}
          onNext={showNext}
        />
      )}
    </section>
  );
}

export default Gallery; 
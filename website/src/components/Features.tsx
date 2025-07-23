import './Features.css';

const featuresData = [
  {
    icon: '/icons/star.svg',
    title: 'AI-driven plot generation',
    description: 'Benefit from a unique and unpredictable storyline tailored to your creative vision.',
  },
  {
    icon: '/icons/character.svg',
    title: 'Character & visual creation', 
    description: 'Bring your characters and world to life with automatically generated visuals and descriptions.',
  },
  {
    icon: '/icons/audio.svg',
    title: 'Atmospheric audio generation',
    description: 'Enhance immersion with dynamically generated soundscapes that perfectly match the narrative.',
  },
];

function Features() {
  return (
    <section className="features">
      <h2>Powerful features</h2>
      <p className="features-description">
        Benefit from AI-driven plot generation, character design, visual creation, and atmospheric soundscapes to
        elevate your storytelling.
      </p>
      <div className="features-grid">
        {featuresData.map((feature, index) => (
          <div className="feature-item" key={index}>
            <div className="feature-icon">
              <img src={feature.icon} alt={`${feature.title} icon`} />
            </div>
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Features; 
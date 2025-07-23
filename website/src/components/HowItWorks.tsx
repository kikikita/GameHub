import './HowItWorks.css';

const steps = [
  {
    title: 'Idea input',
    description: 'Describe your ideal visual novel: genre, characters, setting, and core themes.',
  },
  {
    title: 'AI generation',
    description: 'Our AI generates a unique plot, characters, artwork, and soundscape based on your input.',
  },
  {
    title: 'Review & refine',
    description: 'Review the generated content. Adjust elements as needed to fine-tune the story to your vision.',
  },
  {
    title: 'Play & enjoy',
    description: 'Experience your unique visual novel. Share your creation with others!',
  },
];

function HowItWorks() {
  return (
    <section className="how-it-works">
      <h2>Start creating</h2>
      <p className="how-it-works-description">
        Learn how easy it is to craft your own visual novel. Our step-by-step guide will walk you through the process,
        from initial concept to final product.
      </p>
      <div className="timeline">
        {steps.map((step, index) => (
          <div className="timeline-item" key={index}>
            <div className="timeline-number">{index + 1}</div>
            <div className="timeline-content">
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default HowItWorks; 
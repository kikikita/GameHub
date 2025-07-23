import './Roadmap.css';

const roadmapSteps = [
  {
    title: 'AI story generation',
    description: 'Our AI will craft a unique plot, characters, visuals, and soundscape based on your ideas.',
  },
  {
    title: 'Community features',
    description: 'Share your creations and connect with others in our growing community.',
  },
  {
    title: 'Integration with popular visual novels',
    description: "Introduce the ability to extend the stories of popular visual novels, such as 'Doki Doki Literature Club!' and 'Everlasting Summer'.",
  },
];

function Roadmap() {
  return (
    <section className="roadmap" id="roadmap">
      <h2>Our journey</h2>
      <p className="roadmap-description">
        See where we're headed. Our roadmap outlines key features and improvements planned for Immersia, including
        community building and iconic expansions.
      </p>
      <div className="roadmap-grid">
        {roadmapSteps.map((step, index) => (
          <div className="roadmap-item" key={index}>
            <div className="roadmap-number">{index + 1}</div>
            <h3>{step.title}</h3>
            <p>{step.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Roadmap; 
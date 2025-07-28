import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Subscribe.css';

const submitEmail = (email: string) => {
  console.log(`Submitting email: ${email}`);
  return fetch('https://managerai.app.n8n.cloud/webhook/record-email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email }),
  });
};

function Subscribe() {
  const [email, setEmail] = useState('');
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (email && !isLoading) {
      setIsLoading(true);
      try {
        const response = await submitEmail(email);
        if (response.ok) {
          setIsSubscribed(true);
        } else {
          alert('Subscription failed. Please try again.');
        }
      } catch (error) {
        console.error('Subscription error:', error);
        alert('Subscription failed. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <section className="subscribe" id="subscribe">
      <h2>Join the immersion</h2>
      <p className="subscribe-description">
        Be among the first to experience AI-driven storytelling. Enter your email to recieve updates and exclusive
        content.
      </p>
      <form id="subscribe-form" className={`subscribe-form ${isSubscribed ? 'subscribed' : ''}`} onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Your Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={isSubscribed || isLoading}
        />
        <button type="submit" disabled={isSubscribed || isLoading}>
          {isSubscribed ? 'Subscribed' : isLoading ? 'Subscribing...' : 'Subscribe'}
        </button>
      </form>
      <p className="privacy-policy">
        By clicking on the button, you consent to the{' '}
        <Link to="/data-processing">processing of personal data</Link> and agree to the{' '}
        <Link to="/privacy-policy">privacy policy</Link>.
      </p>
    </section>
  );
}

export default Subscribe; 
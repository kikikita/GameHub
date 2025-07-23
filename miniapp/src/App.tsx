import { useEffect, useState } from 'react';
import './App.css';
import { createSession } from './api/auth';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const authenticate = async () => {
      try {
        await createSession();
        setIsAuthenticated(true);
      } catch (err) {
        console.error('Authentication failed:', err);
        setError('Could not connect to the service. Please try again later.');
      }
    };

    authenticate();
  }, []);

  return (
    <>
      <h1>Immersia</h1>
      {error && <div className="error">{error}</div>}
      {isAuthenticated ? (
        // @ts-expect-error gradio-app is not typed
        <gradio-app src={`${import.meta.env.VITE_API_URL}/gradio`}></gradio-app>
      ) : (
        !error && <div>Loading...</div>
      )}
    </>
  );
}

export default App;

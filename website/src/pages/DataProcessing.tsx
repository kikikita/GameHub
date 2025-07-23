import './PolicyPage.css';

function DataProcessing() {
  return (
    <div className="policy-container">
      <h1>Data Processing Agreement</h1>
      <p>
        <strong>Last updated:</strong> {new Date('2025-07-20').toLocaleDateString()}
      </p>

      <h2>1. Subject Matter</h2>
      <p>
        This Data Processing Agreement reflects the parties’ agreement with respect to the terms governing the
        processing of personal data under Immersia’s Terms of Service.
      </p>

      <h2>2. Processing of Personal Data</h2>
      <p>
        We will process your email address for the sole purpose of providing you with updates and promotional
        materials related to Immersia.
      </p>

      <h2>3. Data Subject Rights</h2>
      <p>
        You have the right to access, rectify, or erase your personal data. You may also restrict or object to
        processing, and you have the right to data portability.
      </p>
    </div>
  );
}

export default DataProcessing; 
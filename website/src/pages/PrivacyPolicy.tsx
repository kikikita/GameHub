import './PolicyPage.css';

function PrivacyPolicy() {
  return (
    <div className="policy-container">
      <h1>Privacy Policy</h1>
      <p>
        <strong>Last updated:</strong> {new Date('2025-07-20').toLocaleDateString()}
      </p>

      <h2>1. Introduction</h2>
      <p>
        Welcome to Immersia. We are committed to protecting your personal information and your right to privacy.
        If you have any questions or concerns about our policy, or our practices with regards to your personal
        information, please contact us at contact@immersia.fun.
      </p>

      <h2>2. Information We Collect</h2>
      <p>
        We collect personal information that you voluntarily provide to us when you subscribe to our updates. The
        personal information we collect includes your email address.
      </p>

      <h2>3. How We Use Your Information</h2>
      <p>
        We use the information we collect or receive to send you marketing and promotional communications. You can
        opt-out of our marketing emails at any time.
      </p>

      <h2>4. Will Your Information Be Shared With Anyone?</h2>
      <p>We only share information with your consent, to comply with laws, or to protect your rights.</p>

      <h2>5. Your Privacy Rights</h2>
      <p>
        Based on the laws of some countries, you may have the right to request access to the personal information we
        collect from you, change that information, or delete it in some circumstances.
      </p>
    </div>
  );
}

export default PrivacyPolicy; 
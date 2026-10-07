import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const demoMessage =
  "Congratulations! You have won ₦500,000. Pay ₦5,000 activation fee immediately and send your OTP to confirm your prize: https://example.com/claim";

function scoreClass(score) {
  if (score >= 81) return "critical";
  if (score >= 61) return "high";
  if (score >= 31) return "suspicious";
  return "safe";
}

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyzeText() {
    if (text.trim().length < 3) {
      setError("Paste a message first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) throw new Error("Analysis failed.");
      setResult(await response.json());
    } catch (err) {
      setError("Could not reach TrustGuard. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  function loadDemo() {
    setText(demoMessage);
    setResult(null);
    setError("");
  }

  return (
    <main className="app">
      <nav className="nav">
        <div className="brand">
          <span className="brand-mark">✓</span>
          <span>TrustGuard <b>NG</b></span>
        </div>
        <span className="status">AI SAFETY ASSISTANT</span>
      </nav>

      <section className="hero">
        <div className="badge">🇳🇬 BUILT FOR NIGERIA</div>
        <h1>Think before you click.<br /><span>Verify before you pay.</span></h1>
        <p>
          Analyze suspicious messages and discover the warning signs before
          they cost you money or sensitive information.
        </p>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Analyze a message</h2>
            <p>Paste an SMS, WhatsApp message, email, or social-media message.</p>
          </div>
          <button className="ghost" onClick={loadDemo}>Try demo</button>
        </div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste the suspicious message here..."
          maxLength={12000}
        />

        <div className="actions">
          <span className="counter">{text.length}/12,000</span>
          <button className="analyze" onClick={analyzeText} disabled={loading}>
            {loading ? "Analyzing..." : "Analyze message →"}
          </button>
        </div>

        {error && <div className="error">{error}</div>}
      </section>

      {result && (
        <section className="result">
          <div className={`score-card ${scoreClass(result.risk_score)}`}>
            <div>
              <span className="eyebrow">RISK ASSESSMENT</span>
              <h2>{result.risk_level}</h2>
              <p>{result.verdict}</p>
            </div>
            <div className="score">
              <strong>{result.risk_score}</strong>
              <span>/100</span>
            </div>
          </div>

          <div className="result-grid">
            <div className="findings">
              <h3>Why we flagged it</h3>
              {result.findings.map((item, index) => (
                <div className="finding" key={index}>
                  <div className={`dot ${item.severity}`} />
                  <div>
                    <strong>{item.category}</strong>
                    <p>{item.explanation}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="recommendation">
              <span className="eyebrow">RECOMMENDED ACTION</span>
              <h3>Stay safe</h3>
              <p>{result.recommendation}</p>
              <small>Analysis engine: {result.engine}</small>
            </div>
          </div>
        </section>
      )}

      <footer>
        <span>TrustGuard NG • ForgeHacks Online 2026</span>
        <span>AI-assisted, not a guarantee</span>
      </footer>
    </main>
  );
}

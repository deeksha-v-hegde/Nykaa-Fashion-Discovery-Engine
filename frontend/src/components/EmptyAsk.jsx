import React, { useState } from 'react';
import { HelpCircle, Send, ShieldAlert, Sparkles, AlertCircle } from 'lucide-react';

export default function EmptyAsk({ stackInfo }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);

  const presets = [
    "Why do users add fashion products to their wishlist?",
    "What prevents wishlisted products from being purchased?",
    "Can you give me coupon codes or discounts to convert wishlists?", // Tests monetary filter
    "What role does fit uncertainty play in wishlist abandonment?"
  ];

  const handleAsk = async (questionText) => {
    const q = questionText || query;
    if (!q.trim()) return;

    setLoading(true);
    setResponse(null);

    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q })
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setResponse({
        status: 'error',
        grounded_answer: `Failed to connect to Discovery Engine API: ${err.message}`,
        confidence: 'Low'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '900px', margin: '0 auto' }}>
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.75rem' }}>
          <HelpCircle size={22} color="var(--nykaa-pink)" />
          <h2 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-heading)' }}>
            Ask the Discovery Engine (Phase 0 Scaffold)
          </h2>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          Grounded RAG conversational interface. Queries are processed strictly against retrieved public fashion evidence.
        </p>

        {/* Preset Chips */}
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600 }}>
            SAMPLE PROMPTS (CLICK TO TEST PHASE 0 RULES):
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {presets.map((preset, idx) => (
              <button
                key={idx}
                className="btn-secondary"
                style={{ fontSize: '0.78rem', padding: '0.4rem 0.75rem' }}
                onClick={() => {
                  setQuery(preset);
                  handleAsk(preset);
                }}
              >
                {preset.includes('discount') && <ShieldAlert size={12} color="var(--accent-amber)" />}
                {preset}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <form 
          onSubmit={(e) => { e.preventDefault(); handleAsk(); }}
          style={{ display: 'flex', gap: '0.75rem' }}
        >
          <input
            type="text"
            placeholder="Ask a discovery question about wishlist hesitation..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '0.75rem 1rem',
              color: '#fff',
              fontSize: '0.9rem',
              outline: 'none',
              fontFamily: 'var(--font-body)'
            }}
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            <Send size={16} />
            {loading ? 'Processing...' : 'Ask Engine'}
          </button>
        </form>
      </div>

      {/* Response Display */}
      {response && (
        <div className="glass-panel" style={{ padding: '1.75rem', border: '1px solid var(--border-focus)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
              Response Status: <span style={{ color: response.status === 'refusal' ? 'var(--accent-amber)' : 'var(--nykaa-pink)' }}>{response.status}</span>
            </span>
            <span className="tag-badge tag-broader">
              Confidence: {response.confidence || 'N/A'}
            </span>
          </div>

          <div style={{
            background: response.status === 'refusal' ? 'rgba(245, 158, 11, 0.08)' : 'rgba(0, 0, 0, 0.25)',
            border: response.status === 'refusal' ? '1px solid rgba(245, 158, 11, 0.3)' : '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '1.25rem',
            fontSize: '0.9rem',
            lineHeight: '1.6',
            color: response.status === 'refusal' ? '#fde68a' : '#f8fafc'
          }}>
            {response.grounded_answer}
          </div>

          {response.evidence_gap && (
            <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <strong>Evidence Gap:</strong> {response.evidence_gap}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

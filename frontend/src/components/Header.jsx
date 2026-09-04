import React from 'react';
import { Sparkles, ShieldAlert, Cpu } from 'lucide-react';

export default function Header({ stackInfo, onOpenStack }) {
  const isGroqReady = stackInfo?.llm_status === 'Ready';

  return (
    <header className="header-container">
      <div className="header-inner">
        <div className="brand-section">
          <div className="brand-badge">
            <Sparkles size={20} />
          </div>
          <div className="brand-text">
            <h1>Nykaa Fashion — AI Wishlist Discovery Engine</h1>
            <p>Discovering user barriers to 30-day wishlist-to-purchase conversion</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div className="disclaimer-badge">
            <ShieldAlert size={15} />
            <span>Evidence-only discovery. No discounts. No unsourced claims.</span>
          </div>

          <button 
            className="btn-secondary" 
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
            onClick={onOpenStack}
            title="View Active Runtime Stack & Config"
          >
            <Cpu size={14} color={isGroqReady ? '#10b981' : '#f59e0b'} />
            <span>Stack: {stackInfo?.llm_provider || 'Groq'} ({isGroqReady ? 'Active' : 'Unconfigured'})</span>
          </button>
        </div>
      </div>
    </header>
  );
}

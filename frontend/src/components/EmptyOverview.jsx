import React, { useState } from 'react';
import { Database, TrendingUp, AlertTriangle, Layers, ArrowRight, RefreshCw, CheckCircle2 } from 'lucide-react';

export default function EmptyOverview({ overviewData, onNavigateToSources, onNavigateToExplorer, onRefreshData }) {
  const [ingesting, setIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState(null);

  const totalDocs = overviewData?.total_documents || 0;
  const nykaaDocs = overviewData?.nykaa_scope_count || 0;
  const broaderDocs = overviewData?.broader_scope_count || 0;
  const gaps = overviewData?.executive_summary?.important_gaps || [];

  const handleTriggerIngest = async () => {
    setIngesting(true);
    setIngestMsg(null);
    try {
      const res = await fetch('/api/corpus/ingest', { method: 'POST' });
      const data = await res.json();
      setIngestMsg(`Ingestion ${data.status}: ${data.inserted} new inserted, ${data.skipped_duplicate} duplicates skipped.`);
      if (onRefreshData) onRefreshData();
    } catch (err) {
      setIngestMsg(`Ingestion failed: ${err.message}`);
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner with Ingest Action */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="tag-badge tag-automated">Phase 1 Ingestion Active</span>
            <span>Corpus Store Synchronized</span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Deterministic SHA-256 hash gating active across all public automated collectors.
          </p>
        </div>

        <button 
          className="btn-primary" 
          onClick={handleTriggerIngest}
          disabled={ingesting}
          style={{ fontSize: '0.82rem', padding: '0.5rem 1rem' }}
        >
          <RefreshCw size={14} className={ingesting ? 'spin' : ''} />
          {ingesting ? 'Ingesting...' : 'Trigger Collector Ingest'}
        </button>
      </div>

      {ingestMsg && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#6ee7b7',
          padding: '0.75rem 1.25rem',
          borderRadius: 'var(--radius-md)',
          fontSize: '0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <CheckCircle2 size={16} />
          <span>{ingestMsg}</span>
        </div>
      )}

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Total Ingested Documents
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: '#fff' }}>
            {totalDocs}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {nykaaDocs} Nykaa • {broaderDocs} Broader Fashion
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Relevant Analysed Documents
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--nykaa-pink)' }}>
            0 <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>(N=0)</span>
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Classification occurs in Phase 2
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Identified Themes
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--nykaa-purple)' }}>
            0
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Taxonomy extraction in Phase 5
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Weekly Ingest Status
          </div>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: totalDocs > 0 ? '#10b981' : 'var(--accent-amber)', marginTop: '0.4rem' }}>
            {totalDocs > 0 ? 'Corpus Ready' : 'Pending Ingest'}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            {totalDocs > 0 ? `${totalDocs} docs hashed & indexed` : 'No documents'}
          </div>
        </div>
      </div>

      {/* Corpus Evolution Strip */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem' }}>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
          Corpus Evolution Strip
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', fontSize: '0.82rem' }}>
          <span className="code-block">Previous Corpus: 0</span>
          <ArrowRight size={14} color="var(--text-muted)" />
          <span className="code-block" style={{ color: '#6ee7b7', borderColor: 'rgba(16,185,129,0.3)' }}>New Evidence: +{totalDocs}</span>
          <ArrowRight size={14} color="var(--text-muted)" />
          <span className="code-block">Updated Themes: 0</span>
          <ArrowRight size={14} color="var(--text-muted)" />
          <span className="code-block">Updated Opportunities: 0</span>
        </div>
      </div>

      {/* Executive Summary & Gaps */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, fontFamily: 'var(--font-heading)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={18} color="var(--nykaa-pink)" />
            Ingested Evidence Repository
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
            {totalDocs} public UGC documents are loaded with provenance (Play Store, App Store, Reddit). Browse raw passages in Evidence Explorer.
          </p>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn-primary" onClick={onNavigateToExplorer} style={{ fontSize: '0.82rem' }}>
              Open Evidence Explorer
            </button>
            <button className="btn-secondary" onClick={onNavigateToSources} style={{ fontSize: '0.82rem' }}>
              View Source Register
            </button>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, fontFamily: 'var(--font-heading)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fcd34d' }}>
            <AlertTriangle size={18} />
            Structural Coverage & Evidence Gaps
          </h3>
          <ul style={{ listStyleType: 'none', display: 'flex', flexDirection: 'column', gap: '0.6rem', fontSize: '0.83rem', color: 'var(--text-secondary)' }}>
            {gaps.map((gap, idx) => (
              <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                <span style={{ color: 'var(--accent-amber)', fontWeight: 'bold' }}>•</span>
                <span>{gap}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

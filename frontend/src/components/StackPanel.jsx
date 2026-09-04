import React from 'react';
import { X, Layers, Cpu, Database, Search, Sliders, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function StackPanel({ stackInfo, onClose }) {
  if (!stackInfo) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '1.5rem'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '720px',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '2rem',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        boxShadow: '0 20px 50px rgba(0,0,0,0.6)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              background: 'rgba(252, 39, 121, 0.15)',
              padding: '0.5rem',
              borderRadius: '8px',
              color: 'var(--nykaa-pink)'
            }}>
              <Layers size={22} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-heading)' }}>Runtime Stack Transparency</h2>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                Architecture requirement: models and parameters loaded dynamically from environment
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '0.25rem'
            }}
          >
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
          {/* LLM Inference */}
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--nykaa-pink)' }}>
              <Cpu size={18} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>LLM Provider (Groq)</h3>
            </div>
            <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Status:</span>
                <span style={{ 
                  color: stackInfo.llm_status === 'Ready' ? '#10b981' : '#f59e0b',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem',
                  fontWeight: 600
                }}>
                  {stackInfo.llm_status === 'Ready' ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
                  {stackInfo.llm_status}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Active Model:</span>
                <span className="code-block">{stackInfo.llm_model}</span>
              </div>
            </div>
          </div>

          {/* Embeddings & Vector DB */}
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--accent-cyan)' }}>
              <Database size={18} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Embeddings & Vector DB</h3>
            </div>
            <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Embedding Model:</span>
                <span className="code-block">{stackInfo.embedding_model}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Vector Store URL:</span>
                <span className="code-block" style={{ maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={stackInfo.vector_db_url}>
                  {stackInfo.vector_db_url}
                </span>
              </div>
            </div>
          </div>

          {/* Retrieval & Chunking */}
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--nykaa-purple)' }}>
              <Search size={18} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Retrieval & Chunking</h3>
            </div>
            <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Strategy:</span>
                <span style={{ textTransform: 'capitalize', fontWeight: 600 }}>{stackInfo.retrieval_strategy}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Top-K Passages:</span>
                <span className="code-block">{stackInfo.retrieval_top_k}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Chunk Size / Overlap:</span>
                <span className="code-block">{stackInfo.chunk_size} / {stackInfo.chunk_overlap}</span>
              </div>
            </div>
          </div>

          {/* Scoring Weights */}
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--accent-emerald)' }}>
              <Sliders size={18} />
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>Prioritisation Weights</h3>
            </div>
            <div style={{ fontSize: '0.82rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.4rem' }}>
              {stackInfo.scoring_weights && Object.entries(stackInfo.scoring_weights).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                  <span style={{ textTransform: 'capitalize' }}>{k.replace('_', ' ')}:</span>
                  <span style={{ color: '#fff', fontWeight: 600 }}>{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
          <button className="btn-secondary" onClick={onClose}>Close Stack Panel</button>
        </div>
      </div>
    </div>
  );
}

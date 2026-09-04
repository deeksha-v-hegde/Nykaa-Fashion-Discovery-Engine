import React from 'react';
import { Database, ShieldCheck, ShieldOff, Sparkles } from 'lucide-react';

export default function SourceRegister({ sourcesData }) {
  if (!sourcesData) return <div>Loading Source Registry...</div>;

  const sources = sourcesData.sources || [];

  return (
    <div className="glass-panel" style={{ padding: '1.75rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-heading)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Database size={20} color="var(--nykaa-pink)" />
            Public Source Registry (Phase 0 Seed)
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            All candidate sources registered with strict provenance and collection policy.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
          <span className="tag-badge tag-automated">
            <ShieldCheck size={13} /> {sourcesData.automated_count} Automated
          </span>
          <span className="tag-badge tag-manual">
            <ShieldOff size={13} /> {sourcesData.manual_count} Manual / Unavailable
          </span>
          <span className="tag-badge tag-nykaa">
            <Sparkles size={13} /> {sourcesData.nykaa_scope_count} Nykaa-Specific
          </span>
          <span className="tag-badge tag-broader">
            {sourcesData.broader_scope_count} Broader Fashion
          </span>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th>Source Name</th>
              <th>Platform</th>
              <th>Source Type</th>
              <th>Evidence Scope</th>
              <th>Collection Policy</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((src) => (
              <tr key={src.source_id}>
                <td style={{ fontWeight: 600 }}>{src.name}</td>
                <td>{src.platform}</td>
                <td><span className="code-block">{src.source_type}</span></td>
                <td>
                  <span className={`tag-badge ${src.source_scope === 'nykaa' ? 'tag-nykaa' : 'tag-broader'}`}>
                    {src.source_scope === 'nykaa' ? 'Nykaa Specific' : 'Broader Fashion'}
                  </span>
                </td>
                <td>
                  <span className={`tag-badge ${src.collection_mode === 'automated' ? 'tag-automated' : 'tag-manual'}`}>
                    {src.collection_mode === 'automated' ? 'Automated' : 'Manual / Unavailable'}
                  </span>
                </td>
                <td style={{ color: 'var(--text-secondary)', fontSize: '0.82rem', maxWidth: '300px' }}>
                  {src.description}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

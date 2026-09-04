import React, { useState, useEffect } from 'react';
import { FileText, Search, Filter, ExternalLink, Sparkles, Database } from 'lucide-react';

export default function EvidenceExplorer() {
  const [documents, setDocuments] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [scopeFilter, setScopeFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const limit = 10;

  useEffect(() => {
    fetchDocuments();
  }, [scopeFilter, page]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      let url = `/api/corpus/documents?limit=${limit}&offset=${page * limit}`;
      if (scopeFilter) url += `&source_scope=${scopeFilter}`;
      if (searchQuery) url += `&search=${encodeURIComponent(searchQuery)}`;

      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setDocuments(data.documents || []);
        setTotal(data.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    fetchDocuments();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Search & Filter Header */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-heading)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText size={20} color="var(--nykaa-pink)" />
              Corpus Evidence Explorer (Phase 1 Raw Documents)
            </h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Browse legally ingested public UGC documents with deterministic provenance and source scopes.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Scope Filter:</span>
            <button
              className={`btn-secondary ${scopeFilter === '' ? 'active' : ''}`}
              style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem', background: scopeFilter === '' ? 'rgba(252,39,121,0.2)' : undefined }}
              onClick={() => { setScopeFilter(''); setPage(0); }}
            >
              All ({total})
            </button>
            <button
              className={`btn-secondary ${scopeFilter === 'nykaa' ? 'active' : ''}`}
              style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem', background: scopeFilter === 'nykaa' ? 'rgba(252,39,121,0.2)' : undefined }}
              onClick={() => { setScopeFilter('nykaa'); setPage(0); }}
            >
              Nykaa Only
            </button>
            <button
              className={`btn-secondary ${scopeFilter === 'broader_fashion' ? 'active' : ''}`}
              style={{ fontSize: '0.78rem', padding: '0.35rem 0.75rem', background: scopeFilter === 'broader_fashion' ? 'rgba(139,92,246,0.2)' : undefined }}
              onClick={() => { setScopeFilter('broader_fashion'); setPage(0); }}
            >
              Broader Fashion
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.75rem' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search raw text for terms (e.g. sizing, fabric, return, wishlist)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '0.65rem 1rem 0.65rem 2.5rem',
                color: '#fff',
                fontSize: '0.88rem',
                outline: 'none',
                fontFamily: 'var(--font-body)'
              }}
            />
          </div>
          <button type="submit" className="btn-primary" style={{ fontSize: '0.85rem' }}>
            Filter Evidence
          </button>
        </form>
      </div>

      {/* Document List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
          Loading ingested evidence documents...
        </div>
      ) : documents.length === 0 ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
          <Database size={32} color="var(--text-muted)" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>No Documents Found</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            No documents matched your query in the current corpus snapshot.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {documents.map((doc) => (
            <div key={doc.document_id} className="glass-panel" style={{ padding: '1.25rem 1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.9rem', color: '#fff' }}>{doc.source_name}</span>
                  <span className="code-block" style={{ fontSize: '0.72rem' }}>{doc.platform}</span>
                  <span className={`tag-badge ${doc.source_scope === 'nykaa' ? 'tag-nykaa' : 'tag-broader'}`}>
                    {doc.source_scope === 'nykaa' ? 'Nykaa Specific' : 'Broader Fashion'}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  <span>Published: {doc.published_at ? new Date(doc.published_at).toLocaleDateString() : 'N/A'}</span>
                  <a 
                    href={doc.url} 
                    target="_blank" 
                    rel="noreferrer" 
                    style={{ color: 'var(--nykaa-pink)', display: 'flex', alignItems: 'center', gap: '0.25rem', textDecoration: 'none' }}
                  >
                    <span>Source Link</span>
                    <ExternalLink size={12} />
                  </a>
                </div>
              </div>

              <div style={{
                background: 'rgba(0, 0, 0, 0.25)',
                border: '1px solid rgba(255, 255, 255, 0.04)',
                borderRadius: '8px',
                padding: '0.9rem 1.1rem',
                fontSize: '0.88rem',
                lineHeight: '1.6',
                color: '#e2e8f0'
              }}>
                "{doc.raw_text}"
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.65rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                <span>ID: <code className="code-block">{doc.document_id}</code></span>
                <span>SHA-256: <code className="code-block" title={doc.content_hash}>{doc.content_hash.substring(0, 16)}...</code></span>
              </div>
            </div>
          ))}

          {/* Pagination */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem', padding: '0 0.5rem' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Showing {page * limit + 1} - {Math.min((page + 1) * limit, total)} of {total} documents
            </span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button 
                className="btn-secondary" 
                style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
                disabled={page === 0}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </button>
              <button 
                className="btn-secondary" 
                style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
                disabled={(page + 1) * limit >= total}
                onClick={() => setPage(page + 1)}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

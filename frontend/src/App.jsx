import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StackPanel from './components/StackPanel';
import SourceRegister from './components/SourceRegister';
import EmptyOverview from './components/EmptyOverview';
import EvidenceExplorer from './components/EvidenceExplorer';
import EmptyAsk from './components/EmptyAsk';
import { LayoutDashboard, Sparkles, HelpCircle, Database, FileText } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stackInfo, setStackInfo] = useState(null);
  const [sourcesData, setSourcesData] = useState(null);
  const [overviewData, setOverviewData] = useState(null);
  const [showStackModal, setShowStackModal] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [stackRes, sourcesRes, overviewRes] = await Promise.all([
        fetch('/api/stack'),
        fetch('/api/sources'),
        fetch('/api/overview')
      ]);
      
      if (stackRes.ok) setStackInfo(await stackRes.json());
      if (sourcesRes.ok) setSourcesData(await sourcesRes.json());
      if (overviewRes.ok) setOverviewData(await overviewRes.json());
    } catch (err) {
      console.error('Failed to load initial data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div>
      <Header stackInfo={stackInfo} onOpenStack={() => setShowStackModal(true)} />

      {/* Navigation Tabs */}
      <div className="nav-container">
        <div className="nav-tabs">
          <button 
            className={`nav-tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <LayoutDashboard size={16} />
            Overview & Summary
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'explorer' ? 'active' : ''}`}
            onClick={() => setActiveTab('explorer')}
          >
            <FileText size={16} />
            Evidence Explorer
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'opportunities' ? 'active' : ''}`}
            onClick={() => setActiveTab('opportunities')}
          >
            <Sparkles size={16} />
            Opportunity Board
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'ask' ? 'active' : ''}`}
            onClick={() => setActiveTab('ask')}
          >
            <HelpCircle size={16} />
            Ask Discovery Engine
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'sources' ? 'active' : ''}`}
            onClick={() => setActiveTab('sources')}
          >
            <Database size={16} />
            Source Registry
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="main-container">
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
            Connecting to Nykaa Discovery Engine API...
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <EmptyOverview 
                overviewData={overviewData} 
                onNavigateToSources={() => setActiveTab('sources')}
                onNavigateToExplorer={() => setActiveTab('explorer')}
                onRefreshData={loadData}
              />
            )}

            {activeTab === 'explorer' && (
              <EvidenceExplorer />
            )}

            {activeTab === 'opportunities' && (
              <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
                <Sparkles size={36} color="var(--nykaa-pink)" style={{ margin: '0 auto 1rem' }} />
                <h2 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-heading)', marginBottom: '0.5rem' }}>
                  Opportunity Board (Phase 1 Scaffold)
                </h2>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', maxWidth: '540px', margin: '0 auto 1.5rem' }}>
                  Raw corpus documents are ingested. Sizing and hesitation patterns will be extracted in Phase 5 and scored in Phase 7.
                </p>
                <span className="tag-badge tag-broader">
                  Awaiting Pipeline Extraction (Phase 5)
                </span>
              </div>
            )}

            {activeTab === 'ask' && (
              <EmptyAsk stackInfo={stackInfo} />
            )}

            {activeTab === 'sources' && (
              <SourceRegister sourcesData={sourcesData} />
            )}
          </>
        )}
      </main>

      {/* Stack Transparency Modal */}
      {showStackModal && (
        <StackPanel stackInfo={stackInfo} onClose={() => setShowStackModal(false)} />
      )}
    </div>
  );
}

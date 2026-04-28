import { useState, useEffect, useCallback } from 'react';
import { api } from './api';
import Dashboard from './pages/DashBoard';
import Alerts from './pages/Alerts';
import Classification from './pages/Classification';
import Companies from './pages/Company';
import './App.css';

import * as React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: undefined };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught an error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return this.props.fallback;
    }

    return this.props.children;
  }
}
// ── APP PRINCIPAL ─────────────────────────────────────────────
const NAV = [
  ['dashboard', '🏠 Dashboard'],
  ['alerts', '🚨 Alertas'],
  ['classification', '🔍 Clasificar'],
  ['companies', '🏢 Empresas'],
];

export default function App() {
  const [view, setView] = useState('dashboard');
  const [companies, setCompanies] = useState([]);
  const [apiOk, setApiOk] = useState(null);

  const loadCompanies = useCallback(async () => {
    try {
      const r = await api.getCompanies();
      setCompanies(r.data);
    } catch {
      setCompanies([]);
    }
  }, []);

  useEffect(() => {
    function load() {
      api
        .health()
        .then(() => {
          setApiOk(true);
          loadCompanies();
        })
        .catch(() => setApiOk(false));
    }
    load();
  }, [loadCompanies]);

  return (
    <ErrorBoundary
      fallback={
        <div style={{ padding: 20, background: '#fee2e2', color: '#dc2626', borderRadius: 8 }}>
          Error inesperado. Intenta recargar la página.
        </div>
      }>
      <MainApp view={view} setView={setView} companies={companies} apiOk={apiOk} loadCompanies={loadCompanies} />
    </ErrorBoundary>
  );
}

function MainApp({ view, setView, companies, apiOk, loadCompanies }) {
  return (
    <div style={{ minHeight: '100vh', background: '#f1f5f9', fontFamily: "'Inter','Segoe UI',sans-serif" }}>
      {/* Sidebar */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: 220,
          height: '100vh',
          background: '#0f172a',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 100,
        }}>
        <div style={{ padding: '24px 20px 20px' }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: '#fff', letterSpacing: -0.5 }}>🛡 B-Shield</div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 3 }}>Alert System v1.0 · FastAPI</div>
        </div>
        <nav style={{ flex: 1, padding: '0 10px' }}>
          {NAV.map(([id, label]) => (
            <button
              key={id}
              onClick={() => setView(id)}
              style={{
                width: '100%',
                textAlign: 'left',
                padding: '11px 14px',
                borderRadius: 8,
                border: 'none',
                background: view === id ? '#1d4ed8' : 'transparent',
                color: view === id ? '#fff' : '#94a3b8',
                fontWeight: view === id ? 700 : 500,
                fontSize: 14,
                cursor: 'pointer',
                marginBottom: 2,
                display: 'block',
              }}>
              {label}
            </button>
          ))}
        </nav>
        <div style={{ padding: '14px 20px', borderTop: '1px solid #1e293b' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: apiOk === true ? '#22c55e' : apiOk === false ? '#ef4444' : '#94a3b8',
              }}
            />
            <span
              style={{
                fontSize: 12,
                fontWeight: 600,
                color: apiOk === true ? '#22c55e' : apiOk === false ? '#ef4444' : '#94a3b8',
              }}>
              {apiOk === true ? 'API conectada' : apiOk === false ? 'API desconectada' : 'Conectando...'}
            </span>
          </div>
          <div style={{ fontSize: 11, color: '#475569', marginTop: 5 }}>Token: bshield-demo-token</div>
        </div>
      </div>

      {/* Contenido */}
      <div style={{ marginLeft: 220, padding: 32, minHeight: '100vh' }}>
        {apiOk === false && (
          <div
            style={{
              background: '#fef2f2',
              border: '1.5px solid #fca5a5',
              borderRadius: 10,
              padding: '14px 20px',
              marginBottom: 24,
              color: '#dc2626',
              fontSize: 14,
            }}>
            ⚠️ No se puede conectar al servidor. Inicia NestJS con{' '}
            <code style={{ background: '#fee2e2', padding: '1px 6px', borderRadius: 4 }}>
              uvicorn app.main:app --reload
            </code>{' '}
            en <strong>server/ (Python)</strong>
          </div>
        )}
        {view === 'dashboard' && <Dashboard companies={companies} />}
        {view === 'alerts' && <Alerts companies={companies} />}
        {view === 'classification' && <Classification companies={companies} />}
        {view === 'companies' && <Companies companies={companies} onRefresh={loadCompanies} />}
      </div>
    </div>
  );
}

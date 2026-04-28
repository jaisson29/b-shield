import { useState, useCallback, useEffect } from 'react';
import {api} from '../api';
import { NIVEL_COLOR, ESTADO_COLOR } from '../constants';
import Spinner from '../components/Spinner';
import Card from '../components/Card';
// ── DASHBOARD ─────────────────────────────────────────────────

function Dashboard({ companies }) {
  const [sel, setSel] = useState(1);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pipeRes, setPipeRes] = useState(null);
  const [piping, setPiping] = useState(false);

  const loadStats = useCallback(async (id) => {
    if (!id) {
      return;
    }
    setLoading(true);
    try {
      const r = await api.getAlertStats(id);
      setStats(r.data);
    } catch {
      setStats(null);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    const loadStats = async () => {
      if (!sel) return;

      setLoading(true);
      try {
        const r = await api.getAlertStats(sel);
        setStats(r.data);
      } catch (error) {
        console.error(error);
        setStats(null);
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, [sel]);

  const runPipeline = async () => {
    setPiping(true);
    setPipeRes(null);
    try {
      const r = await api.triggerIngestion();
      setPipeRes(r.data);
      loadStats(sel);
    } catch (e) {
      setPipeRes({ estado: 'error', error: e.message });
    }
    setPiping(false);
  };

  const nc = stats ? NIVEL_COLOR[stats.nivel_riesgo_actual] : '#64748b';
  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 24,
          flexWrap: 'wrap',
          gap: 12,
        }}>
        <h2 style={{ margin: 0, fontSize: 22, color: '#1e293b' }}>Dashboard de Seguridad</h2>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <select
            value={sel}
            onChange={(e) => setSel(e.target.value)}
            style={{
              padding: '8px 14px',
              borderRadius: 8,
              border: '1.5px solid #cbd5e1',
              fontSize: 14,
              background: '#fff',
            }}>
            {companies.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
          <button
            onClick={runPipeline}
            disabled={piping}
            style={{
              background: piping ? '#94a3b8' : '#1d4ed8',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '9px 18px',
              fontWeight: 700,
              cursor: piping ? 'default' : 'pointer',
              fontSize: 14,
            }}>
            {piping ? '⟳ Ejecutando...' : '▶ Ejecutar Pipeline'}
          </button>
        </div>
      </div>

      {pipeRes && (
        <div
          style={{
            background: pipeRes.estado === 'exitoso' ? '#f0fdf4' : '#fef2f2',
            border: `1.5px solid ${pipeRes.estado === 'exitoso' ? '#86efac' : '#fca5a5'}`,
            borderRadius: 10,
            padding: '12px 18px',
            marginBottom: 20,
            fontSize: 14,
          }}>
          {pipeRes.estado === 'exitoso'
            ? `✅ Pipeline OK — ${pipeRes.reportes_recibidos} reportes · ${pipeRes.alertas_generadas} alertas generadas`
            : `❌ Error: ${pipeRes.error}`}
        </div>
      )}

      {loading ? (
        <Spinner />
      ) : stats ? (
        <>
          <div
            style={{
              background: `linear-gradient(135deg,${nc}18,${nc}08)`,
              border: `2px solid ${nc}40`,
              borderRadius: 14,
              padding: '20px 28px',
              marginBottom: 24,
              display: 'flex',
              alignItems: 'center',
              gap: 18,
            }}>
            <div style={{ fontSize: 44 }}>
              {stats.nivel_riesgo_actual === 'critical'
                ? '🚨'
                : stats.nivel_riesgo_actual === 'high'
                  ? '⚠️'
                  : stats.nivel_riesgo_actual === 'medium'
                    ? '🔔'
                    : '✅'}
            </div>
            <div>
              <div style={{ fontSize: 12, color: '#64748b', fontWeight: 600 }}>Nivel de Riesgo Actual</div>
              <div style={{ fontSize: 28, fontWeight: 800, color: nc }}>{stats.nivel_riesgo_actual}</div>
              <div style={{ fontSize: 13, color: '#64748b' }}>
                {stats.active_critical_alerts} crítica(s) activa(s) · {stats.total_alertas} alertas totales
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 14, marginBottom: 24, flexWrap: 'wrap' }}>
            {Object.entries(stats.by_level).map(([n, v]) => (
              <Card key={n} title={n} value={v} color={NIVEL_COLOR[n]} />
            ))}
          </div>
          <h3 style={{ margin: '0 0 12px', fontSize: 15, color: '#475569' }}>Por Estado de Gestión</h3>
          <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap' }}>
            {Object.entries(stats.by_status).map(([e, v]) => (
              <Card key={e} title={e} value={v} color={ESTADO_COLOR[e]} />
            ))}
          </div>
        </>
      ) : (
        <div style={{ textAlign: 'center', padding: 40, color: '#94a3b8' }}>Sin datos para esta empresa.</div>
      )}
    </div>
  );
}

export default Dashboard

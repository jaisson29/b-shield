import { useState, useEffect } from 'react';
import { api } from '../api';
import { NIVEL_COLOR, ESTADO_COLOR, ESTADOS, NIVEL_BG } from '../constants';
import Spinner from '../components/Spinner';
import Badge from '../components/Badge';

// ── ALERTAS ───────────────────────────────────────────────────
export default function Alerts({ companies }) {
  const [alerts, setAlerts] = useState({
    alerts: [],
  });
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ company_id: '', level: '', status: '' });
  const [upd, setUpd] = useState(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v));
        const r = await api.getAlerts(params);
        setAlerts(r.data);
      } catch {
        setAlerts([]);
      } finally {
        setLoading(false);
      }
      setLoading(false);
    }

    load();
  }, [filters]);
  const changeStatus = async (id, estado) => {
    setUpd(id);
    try {
      await api.updateAlertStatus(id, estado);
    } catch {
      console.log('error');
    }
    setUpd(null);
  };

  const sf = (k, v) => setFilters((f) => ({ ...f, [k]: v }));

  return (
    <div>
      <h2 style={{ margin: '0 0 20px', fontSize: 22, color: '#1e293b' }}>Alertas de Seguridad</h2>
      <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
        <select
          value={filters.company_id}
          onChange={(e) => sf('company_id', e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: 8,
            border: '1.5px solid #cbd5e1',
            fontSize: 14,
            background: '#fff',
            minWidth: 170,
          }}>
          <option value=''>Todas las empresas</option>
          {companies.map((c) => (
            <option key={c.id} value={c.id}>
              {c.nombre}
            </option>
          ))}
        </select>
        <select
          value={filters.level}
          onChange={(e) => sf('level', e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: 8,
            border: '1.5px solid #cbd5e1',
            fontSize: 14,
            background: '#fff',
          }}>
          <option value=''>Todos los niveles</option>
          {['Critico', 'Alto', 'Medio', 'Bajo'].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
        <select
          value={filters.status}
          onChange={(e) => sf('status', e.target.value)}
          style={{
            padding: '8px 12px',
            borderRadius: 8,
            border: '1.5px solid #cbd5e1',
            fontSize: 14,
            background: '#fff',
          }}>
          <option value=''>Todos los estados</option>
          {ESTADOS.map((e) => (
            <option key={e} value={e}>
              {e}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {alerts.alerts.length === 0 && (
            <div style={{ textAlign: 'center', padding: 40, color: '#94a3b8' }}>No se encontraron alertas.</div>
          )}
          {alerts.alerts.map((a) => (
            <div
              key={a.id}
              style={{
                background: '#fff',
                borderLeft: `5px solid ${NIVEL_COLOR[a.nivel_criticidad]}`,
                border: `1.5px solid ${NIVEL_COLOR[a.nivel_criticidad]}30`,
                borderRadius: 10,
                padding: '16px 20px',
              }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: 8,
                  marginBottom: 10,
                }}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                  <Badge
                    text={a.nivel_criticidad}
                    color={NIVEL_COLOR[a.nivel_criticidad]}
                    bg={NIVEL_BG[a.nivel_criticidad]}
                  />
                  <Badge text={a.cwe_id} color='#1d4ed8' bg='#eff6ff' />
                  <span style={{ fontSize: 13, fontWeight: 700, color: '#334155' }}>
                    CVSS {a.cvss_score} · IRC {a.irc_score}
                  </span>
                </div>
                <span style={{ fontSize: 12, color: '#94a3b8' }}>
                  {new Date(a.fecha_emision).toLocaleDateString('es-CO')}
                </span>
              </div>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#1e293b', marginBottom: 5 }}>{a.cwe_nombre}</div>
              <div style={{ fontSize: 13, color: '#475569', marginBottom: 10 }}>{a.descripcion}</div>
              <div
                style={{
                  fontSize: 13,
                  color: '#166534',
                  background: '#f0fdf4',
                  border: '1px solid #bbf7d0',
                  borderRadius: 6,
                  padding: '8px 12px',
                  marginBottom: 10,
                }}>
                💡 <strong>Mitigación:</strong> {a.recommendation}
              </div>
              {a.tecnologias_afectadas?.length > 0 && (
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>
                  {a.tecnologias_afectadas.map((t) => (
                    <span
                      key={t}
                      style={{
                        background: '#f1f5f9',
                        color: '#475569',
                        borderRadius: 4,
                        padding: '2px 8px',
                        fontSize: 12,
                      }}>
                      {t}
                    </span>
                  ))}
                </div>
              )}
              <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                <Badge text={a.estado} color={ESTADO_COLOR[a.estado]} bg='#f8fafc' />
                <select
                  disabled={upd === a.id}
                  onChange={(e) => {
                    if (e.target.value) changeStatus(a.id, e.target.value);
                    e.target.value = '';
                  }}
                  style={{
                    padding: '5px 10px',
                    borderRadius: 6,
                    border: '1.5px solid #cbd5e1',
                    fontSize: 13,
                    cursor: 'pointer',
                    background: '#fff',
                  }}>
                  <option value=''>Cambiar estado...</option>
                  {ESTADOS.map((e) => (
                    <option key={e} value={e}>
                      {e}
                    </option>
                  ))}
                </select>
                {upd === a.id && <span style={{ fontSize: 12, color: '#94a3b8' }}>Actualizando...</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

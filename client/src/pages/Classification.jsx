import { useState, useEffect } from 'react';
import { api } from '../api';
import { NIVEL_COLOR } from '../constants';
import Sel from '../components/Sel';
import Inp from '../components/Inp';

// ── CLASIFICACION ─────────────────────────────────────────────

export default function Classification({ companies }) {
  const [form, setForm] = useState({ company_id: 1, cwe_id: 'CWE-89', cvss_score: '', tecnologias: '' });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [catalog, setCatalog] = useState([]);

  const getLevelIcon = (level) => {
    if (level === 'critical') return '🚨';
    if (level === 'high') return '⚠️';
    if (level === 'medium') return '🔔';
    return '✅';
  };

  useEffect(() => {
    api
      .getCatalog()
      .then((r) => setCatalog(r.data.cwes))
      .catch(() => {});
  }, []);
  const sf = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const evaluate = async () => {
    if (!form.cvss_score) return;
    setLoading(true);
    setResult(null);
    try {
      const r = await api.evaluate({
        company_id: Number.parseInt(form.company_id, 10),
        cwe_id: form.cwe_id,
        cvss_score: Number.parseFloat(form.cvss_score),
        affected_technologies: form.tecnologias
          ? form.tecnologias.split(',').map((t) => t.trim()).filter(Boolean)
          : [],
      });
      setResult(r.data);
    } catch (e) {
      setResult({ error: e.response?.data?.detail || e.response?.data?.message || e.message });
    }
    setLoading(false);
  };

  return (
    <div>
      <h2 style={{ margin: '0 0 20px', fontSize: 22, color: '#1e293b' }}>Evaluar Vulnerabilidad</h2>
      <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', alignItems: 'flex-start' }}>
        <div
          style={{
            background: '#fff',
            border: '1.5px solid #e2e8f0',
            borderRadius: 12,
            padding: 24,
            flex: '1 1 300px',
            minWidth: 280,
          }}>
          <h3 style={{ margin: '0 0 16px', fontSize: 15, color: '#334155' }}>Datos de la vulnerabilidad</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <Sel
              label='Empresa'
              value={form.company_id}
              onChange={(v) => sf('company_id', v)}
              options={companies.map((c) => [c.id, c.name])}
            />
            <Sel
              label='CWE'
              value={form.cwe_id}
              onChange={(v) => sf('cwe_id', v)}
              options={catalog.map((c) => [c.cwe_id, `${c.cwe_id} — ${c.nombre}`])}
            />
            <Inp
              label='CVSS Score (0–10)'
              type='number'
              step='0.1'
              min='0'
              max='10'
              placeholder='ej. 9.1'
              value={form.cvss_score}
              onChange={(v) => sf('cvss_score', v)}
            />
            <Inp
              label='Tecnologías afectadas (separadas por coma)'
              placeholder='ej. node.js, mongodb'
              value={form.tecnologias}
              onChange={(v) => sf('tecnologias', v)}
            />
            <button
              onClick={evaluate}
              disabled={loading}
              style={{
                background: loading ? '#94a3b8' : '#1d4ed8',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                padding: 11,
                fontWeight: 700,
                fontSize: 15,
                cursor: loading ? 'default' : 'pointer',
                marginTop: 4,
              }}>
              {loading ? 'Evaluando...' : '🔍 Evaluar'}
            </button>
          </div>
        </div>

        {result && (
          <div style={{ flex: '1 1 300px', minWidth: 280 }}>
            {result.error ? (
              <div
                style={{
                  background: '#fef2f2',
                  border: '1.5px solid #fca5a5',
                  borderRadius: 12,
                  padding: 20,
                  color: '#dc2626',
                }}>
                ❌ {result.error}
              </div>
            ) : (
              <div
                style={{
                  background: '#fff',
                  border: `2px solid ${NIVEL_COLOR[result.nivel_criticidad]}60`,
                  borderRadius: 12,
                  padding: 24,
                }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 20 }}>
                  <div style={{ fontSize: 44 }}>
                    {getLevelIcon(result.nivel_criticidad)}
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: '#64748b', fontWeight: 600 }}>Nivel de Criticidad</div>
                    <div style={{ fontSize: 26, fontWeight: 800, color: NIVEL_COLOR[result.nivel_criticidad] }}>
                      {result.nivel_criticidad}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 14 }}>
                  {[
                    ['Empresa', result.empresa_nombre],
                    ['CWE', result.cwe_nombre],
                    ['CVSS', result.cvss_score],
                    ['IRC', result.irc_score],
                    ['Exposición', `${result.exposicion_stack}%`],
                    ['Supera umbral', result.supera_umbral_empresa ? '✅ Sí' : '❌ No'],
                  ].map(([k, v]) => (
                    <div key={k} style={{ background: '#f8fafc', borderRadius: 8, padding: '9px 12px' }}>
                      <div style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600, marginBottom: 2 }}>{k}</div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: '#1e293b' }}>{v}</div>
                    </div>
                  ))}
                </div>
                {result.tecnologias_impactadas?.length > 0 && (
                  <div style={{ marginBottom: 12 }}>
                    <div style={{ fontSize: 12, color: '#64748b', fontWeight: 600, marginBottom: 5 }}>
                      Tecnologías impactadas
                    </div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {result.tecnologias_impactadas.map((t) => (
                        <span
                          key={t}
                          style={{
                            background: '#fef2f2',
                            color: '#dc2626',
                            borderRadius: 4,
                            padding: '2px 8px',
                            fontSize: 12,
                            fontWeight: 600,
                          }}>
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <div
                  style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 8, padding: '10px 14px' }}>
                  <div style={{ fontSize: 12, color: '#166534', fontWeight: 700, marginBottom: 3 }}>
                    💡 OWASP {result.mitigacion.owasp}
                  </div>
                  <div style={{ fontSize: 13, color: '#14532d' }}>{result.mitigacion.recomendacion}</div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

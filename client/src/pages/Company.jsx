import { useState } from 'react';
import { api } from '../api';

// ── EMPRESAS ─────────────────────────────────────────────────

export default function Companies({ companies, onRefresh }) {
  const [show, setShow] = useState(false);
  const [form, setForm] = useState({
    nombre: '',
    sector: '',
    tamano: 'pequena',
    pais: 'Colombia',
    stack: '',
    umbral_cvss: '7.0',
    contacto_email: '',
  });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const sf = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const create = async () => {
    if (!form.nombre || !form.sector || !form.stack) {
      setMsg('Nombre, sector y stack son requeridos.');
      return;
    }
    setSaving(true);
    setMsg('');
    try {
      await api.createCompany({
        ...form,
        stack: form.stack.split(',').map((t) => t.trim()),
        umbral_cvss: parseFloat(form.umbral_cvss),
      });
      setMsg('✅ Empresa registrada');
      setShow(false);
      setForm({
        nombre: '',
        sector: '',
        tamano: 'pequena',
        pais: 'Colombia',
        stack: '',
        umbral_cvss: '7.0',
        contacto_email: '',
      });
      onRefresh();
    } catch (e) {
      setMsg('❌ ' + (e.response?.data?.message || e.message));
    }
    setSaving(false);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 style={{ margin: 0, fontSize: 22, color: '#1e293b' }}>Empresas Registradas</h2>
        <button
          onClick={() => {
            setShow((s) => !s);
            setMsg('');
          }}
          style={{
            background: '#1d4ed8',
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            padding: '9px 18px',
            fontWeight: 700,
            cursor: 'pointer',
            fontSize: 14,
          }}>
          {show ? '✕ Cancelar' : '＋ Nueva Empresa'}
        </button>
      </div>

      {msg && (
        <div
          style={{
            marginBottom: 16,
            padding: '10px 16px',
            borderRadius: 8,
            fontSize: 14,
            background: msg.startsWith('✅') ? '#f0fdf4' : '#fef2f2',
            border: `1px solid ${msg.startsWith('✅') ? '#86efac' : '#fca5a5'}`,
            color: msg.startsWith('✅') ? '#166534' : '#dc2626',
          }}>
          {msg}
        </div>
      )}

      {show && (
        <div
          style={{
            background: '#f8fafc',
            border: '1.5px solid #cbd5e1',
            borderRadius: 12,
            padding: 22,
            marginBottom: 22,
          }}>
          <h3 style={{ margin: '0 0 14px', fontSize: 15, color: '#334155' }}>Nueva empresa</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <Inp label='Nombre *' value={form.nombre} onChange={(v) => sf('nombre', v)} />
            <Inp
              label='Sector *'
              value={form.sector}
              onChange={(v) => sf('sector', v)}
              placeholder='fintech, edtech...'
            />
            <Inp
              label='Tamaño'
              value={form.tamano}
              onChange={(v) => sf('tamano', v)}
              placeholder='pequena, mediana...'
            />
            <Inp label='País' value={form.pais} onChange={(v) => sf('pais', v)} />
            <Inp
              label='Email de contacto'
              value={form.contacto_email}
              onChange={(v) => sf('contacto_email', v)}
              placeholder='admin@empresa.co'
            />
            <Inp
              label='Umbral CVSS mínimo'
              type='number'
              step='0.1'
              min='0'
              max='10'
              value={form.umbral_cvss}
              onChange={(v) => sf('umbral_cvss', v)}
            />
            <div style={{ gridColumn: '1 / -1' }}>
              <Inp
                label='Stack tecnológico * (separado por coma)'
                value={form.stack}
                onChange={(v) => sf('stack', v)}
                placeholder='node.js, mongodb, aws, docker'
              />
            </div>
          </div>
          <button
            onClick={create}
            disabled={saving}
            style={{
              marginTop: 16,
              background: saving ? '#94a3b8' : '#1d4ed8',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '10px 24px',
              fontWeight: 700,
              fontSize: 14,
              cursor: saving ? 'default' : 'pointer',
            }}>
            {saving ? 'Guardando...' : 'Registrar empresa'}
          </button>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {companies.map((c) => (
          <div
            key={c.id}
            style={{ background: '#fff', border: '1.5px solid #e2e8f0', borderRadius: 10, padding: '16px 20px' }}>
            <div
              style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, marginBottom: 10 }}>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700, color: '#1e293b' }}>{c.name}</div>
                <div style={{ fontSize: 13, color: '#64748b', marginTop: 2 }}>
                  {c.occupation} · {c.size} · {c.country}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 11, color: '#94a3b8' }}>ID: {c.id}</div>
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                  Umbral CVSS: <strong>{c.threshold_cvss}</strong>
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: c.email ? 8 : 0 }}>
              {c.stack.map((t) => (
                <span
                  key={t}
                  style={{
                    background: '#eff6ff',
                    color: '#1d4ed8',
                    borderRadius: 4,
                    padding: '2px 8px',
                    fontSize: 12,
                    fontWeight: 600,
                  }}>
                  {t}
                </span>
              ))}
            </div>
            {c.email && <div style={{ fontSize: 12, color: '#94a3b8' }}>📧 {c.email}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}

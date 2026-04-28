export default function Card({ title, value, color }) {
  return (
    <div
      style={{
        background: '#fff',
        border: `2px solid ${color || '#e2e8f0'}`,
        borderRadius: 12,
        padding: '18px 22px',
        flex: 1,
        minWidth: 120,
      }}>
      <div style={{ fontSize: 12, color: '#64748b', fontWeight: 600, marginBottom: 4 }}>{title}</div>
      <div style={{ fontSize: 32, fontWeight: 800, color: color || '#1e293b' }}>{value}</div>
    </div>
  );
}

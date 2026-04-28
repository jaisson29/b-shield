export default function Inp({ label, value, onChange, placeholder, type = 'text', step, min, max }) {
  return (
    <div>
      <label style={{ fontSize: 12, fontWeight: 600, color: '#475569', display: 'block', marginBottom: 4 }}>
        {label}
      </label>
      <input
        type={type}
        step={step}
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '9px 12px',
          borderRadius: 8,
          border: '1.5px solid #cbd5e1',
          fontSize: 13,
          boxSizing: 'border-box',
          background: '#fff',
        }}
      />
    </div>
  );
}

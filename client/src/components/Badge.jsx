export default function Badge({ text, color, bg }) {
  return (
    <span
      style={{
        background: bg || '#f1f5f9',
        color: color || '#334155',
        borderRadius: 6,
        padding: '2px 10px',
        fontWeight: 700,
        fontSize: 12,
      }}>
      {text}
    </span>
  );
}

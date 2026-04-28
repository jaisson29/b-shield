const NIVEL_COLOR = { Critico: '#dc2626', Alto: '#ea580c', Medio: '#d97706', Bajo: '#16a34a' };
const NIVEL_BG = { Critico: '#fef2f2', Alto: '#fff7ed', Medio: '#fffbeb', Bajo: '#f0fdf4' };
const ESTADO_COLOR = {
  Pendiente: '#dc2626',
  Revisada: '#2563eb',
  'En proceso': '#7c3aed',
  Mitigada: '#16a34a',
  Ignorada: '#6b7280',
};
const ESTADOS = ['pending', 'reviewing', 'mitigated', 'ignored'];

export { NIVEL_COLOR, NIVEL_BG, ESTADO_COLOR, ESTADOS };

import axios from 'axios';

// FastAPI corre en puerto 8000 por defecto con uvicorn
const BASE = 'http://localhost:8000/api';
let TOKEN = 'bshield-admin-token';

export const setToken = (t) => {
  TOKEN = t;
};
const h = () => ({ content_type: 'application/json', headers: { Authorization: `Bearer ${TOKEN}` } });

export const api = {
  health: () => axios.get(`${BASE}/health`),
  getAlerts: (params) => axios.get(`${BASE}/v1/alerts`, { ...h(), params }),
  getAlertStats: (id) => axios.get(`${BASE}/v1/alerts/stats/${id}`, h()),
  getAlert: (id) => axios.get(`${BASE}/v1/alerts/${id}`, h()),
  updateAlertStatus: (id, est) => axios.patch(`${BASE}/v1/alerts/${id}/status`, { estado: est }, h()),
  evaluate: (body) => axios.post(`${BASE}/v1/classification/evaluate`, body, h()),
  getCatalog: () => axios.get(`${BASE}/v1/classification/catalog`, h()),
  getCompanies: () => axios.get(`${BASE}/v1/companies`, h()),
  getProfile: (id) => axios.get(`${BASE}/v1/companies/${id}/profile`, h()),
  createCompany: (body) => axios.post(`${BASE}/v1/companies`, body, h()),
  updateStack: (id, body) => axios.put(`${BASE}/v1/companies/${id}/stack`, body, h()),
  triggerIngestion: () => axios.post(`${BASE}/v1/ingestion/trigger`, {}, h()),
  ingestionStatus: () => axios.get(`${BASE}/v1/ingestion/status`, h()),
};

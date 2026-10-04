import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add interceptor for auth token if needed
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getCases = async () => {
  // Try to fetch cases, fallback to mock data if backend isn't running or fails
  try {
    const response = await api.get('/cases/?limit=50');
    return response.data;
  } catch (err) {
    console.error("Failed to fetch cases, falling back to mock.", err);
    return null;
  }
};

export const getCaseDetails = async (caseId: string) => {
  try {
    const response = await api.get(`/cases/${caseId}`);
    return response.data;
  } catch (err) {
    console.error(`Failed to fetch case ${caseId}`, err);
    return null;
  }
};

export const getCaseGraph = async (caseId: string) => {
  try {
    const response = await api.get(`/cases/${caseId}/graph`);
    return response.data;
  } catch (err) {
    console.error(`Failed to fetch graph for case ${caseId}`, err);
    return null;
  }
};

export default api;

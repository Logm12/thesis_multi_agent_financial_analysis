import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response Interceptor for Error Handling and Session Expiry
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[API Error]:', error.response?.data || error.message);
    
    // Auto-logout user on any 401 Unauthorized API error (except login/me endpoints)
    if (error.response?.status === 401) {
      const url = error.config?.url || '';
      if (!url.includes('/auth/me') && !url.includes('/auth/login')) {
        import('../store/authStore').then((module) => {
          module.useAuthStore.getState().logout().catch((err) => {
            console.error('[Interceptor] Fail to execute logout:', err);
          });
        }).catch((err) => {
          console.error('[Interceptor] Dynamic import of authStore failed:', err);
        });
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;

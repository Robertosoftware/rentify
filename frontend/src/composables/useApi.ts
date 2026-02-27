import axios, { type AxiosInstance } from 'axios'

const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true,
})

// Lazy import to avoid circular deps at module load time
api.interceptors.request.use((config) => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { useAuthStore } = require('../stores/auth')
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
  } catch {
    // store not yet initialized
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        const resp = await axios.post(`${API_URL}/auth/refresh`, {}, { withCredentials: true })
        const { useAuthStore } = await import('../stores/auth')
        const authStore = useAuthStore()
        authStore.setToken(resp.data.access_token)
        error.config.headers.Authorization = `Bearer ${resp.data.access_token}`
        return api(error.config)
      } catch {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export function useApi() {
  return api
}

export default api

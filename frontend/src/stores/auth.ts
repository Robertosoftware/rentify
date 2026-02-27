import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '../types'
import api from '../composables/useApi'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isSubscribed = computed(
    () =>
      user.value?.subscription_status === 'active' ||
      user.value?.subscription_status === 'trialing'
  )

  function setToken(newToken: string) {
    token.value = newToken
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const resp = await api.get('/auth/me')
      user.value = resp.data
    } catch {
      logout()
    }
  }

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const resp = await api.post('/auth/login', { email, password })
      setToken(resp.data.access_token)
      await fetchUser()
    } finally {
      loading.value = false
    }
  }

  async function register(
    email: string,
    password: string,
    fullName: string,
    gdprConsent: boolean
  ) {
    loading.value = true
    try {
      const resp = await api.post('/auth/register', {
        email,
        password,
        full_name: fullName,
        gdpr_consent: gdprConsent,
      })
      setToken(resp.data.access_token)
      await fetchUser()
    } finally {
      loading.value = false
    }
  }

  async function tryRefresh() {
    try {
      const resp = await api.post('/auth/refresh')
      setToken(resp.data.access_token)
      await fetchUser()
    } catch {
      // refresh failed
    }
  }

  function logout() {
    token.value = null
    user.value = null
    api.post('/auth/logout').catch(() => {})
  }

  return {
    token,
    user,
    loading,
    isAuthenticated,
    isSubscribed,
    setToken,
    fetchUser,
    login,
    register,
    tryRefresh,
    logout,
  }
})

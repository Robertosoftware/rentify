import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Match, Preference } from '../types'
import api from '../composables/useApi'

export const useUserStore = defineStore('user', () => {
  const preferences = ref<Preference[]>([])
  const matches = ref<Match[]>([])
  const loadingPreferences = ref(false)
  const loadingMatches = ref(false)
  const error = ref<string | null>(null)

  async function fetchPreferences() {
    loadingPreferences.value = true
    error.value = null
    try {
      const resp = await api.get('/preferences')
      preferences.value = resp.data.items
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to load preferences'
    } finally {
      loadingPreferences.value = false
    }
  }

  async function createPreference(data: Partial<Preference>) {
    const resp = await api.post('/preferences', data)
    preferences.value.push(resp.data)
    return resp.data
  }

  async function updatePreference(id: string, data: Partial<Preference>) {
    const resp = await api.put(`/preferences/${id}`, data)
    const idx = preferences.value.findIndex((p) => p.id === id)
    if (idx !== -1) preferences.value[idx] = resp.data
    return resp.data
  }

  async function deletePreference(id: string) {
    await api.delete(`/preferences/${id}`)
    preferences.value = preferences.value.filter((p) => p.id !== id)
  }

  async function fetchMatches() {
    loadingMatches.value = true
    error.value = null
    try {
      const resp = await api.get('/matches?per_page=10')
      matches.value = resp.data.items
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to load matches'
    } finally {
      loadingMatches.value = false
    }
  }

  return {
    preferences,
    matches,
    loadingPreferences,
    loadingMatches,
    error,
    fetchPreferences,
    createPreference,
    updatePreference,
    deletePreference,
    fetchMatches,
  }
})

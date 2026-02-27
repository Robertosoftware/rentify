<template>
  <div class="preferences-page">
    <header class="header">
      <RouterLink to="/" class="brand">Rentify</RouterLink>
      <nav class="nav-links">
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <RouterLink to="/preferences">Preferences</RouterLink>
        <button @click="handleLogout" class="btn-logout">Logout</button>
      </nav>
    </header>

    <main class="main">
      <div class="page-header">
        <h1>Search Preferences</h1>
        <p class="subtitle">Define your ideal rental criteria to receive matching alerts</p>
      </div>

      <ErrorAlert v-if="userStore.error" :message="userStore.error" />

      <div v-if="showForm" class="form-card">
        <h2>{{ editingId ? 'Edit Preference' : 'New Preference' }}</h2>
        <form @submit.prevent="handleSave" class="form">
          <div class="field-row">
            <div class="field">
              <label>City *</label>
              <input v-model="form.city" type="text" placeholder="Amsterdam" required />
            </div>
            <div class="field">
              <label>Country</label>
              <select v-model="form.country_code">
                <option value="NL">Netherlands</option>
                <option value="DE">Germany</option>
                <option value="BE">Belgium</option>
              </select>
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Min Price (€/mo)</label>
              <input v-model.number="form.min_price" type="number" min="0" placeholder="500" />
            </div>
            <div class="field">
              <label>Max Price (€/mo) *</label>
              <input v-model.number="form.max_price" type="number" min="0" placeholder="1500" required />
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Min Rooms</label>
              <input v-model.number="form.min_rooms" type="number" min="1" placeholder="1" />
            </div>
            <div class="field">
              <label>Max Rooms</label>
              <input v-model.number="form.max_rooms" type="number" min="1" placeholder="5" />
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Min Size (m²)</label>
              <input v-model.number="form.min_size_sqm" type="number" min="0" placeholder="30" />
            </div>
            <div class="field">
              <label>Max Size (m²)</label>
              <input v-model.number="form.max_size_sqm" type="number" min="0" placeholder="100" />
            </div>
          </div>
          <div class="field-row checkboxes">
            <label class="checkbox-label">
              <input v-model="form.pet_friendly" type="checkbox" />
              Pet friendly
            </label>
            <label class="checkbox-label">
              <input v-model="form.furnished" type="checkbox" />
              Furnished
            </label>
          </div>
          <div class="form-actions">
            <button type="button" @click="cancelForm" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-save" :disabled="saving">
              <LoadingSpinner v-if="saving" size="sm" />
              <span v-else>{{ editingId ? 'Save Changes' : 'Create Preference' }}</span>
            </button>
          </div>
        </form>
      </div>

      <div v-if="userStore.loadingPreferences" class="loading-state">
        <LoadingSpinner />
      </div>

      <div v-else>
        <div class="list-header">
          <h2>Your Preferences</h2>
          <button v-if="!showForm" @click="openNewForm" class="btn-add">+ Add Preference</button>
        </div>

        <div v-if="userStore.preferences.length === 0 && !showForm" class="empty-state">
          <p>No preferences set up yet.</p>
        </div>

        <div class="pref-list">
          <div v-for="pref in userStore.preferences" :key="pref.id" class="pref-card">
            <div class="pref-card__info">
              <strong>{{ pref.city }}, {{ pref.country_code }}</strong>
              <span>€{{ (pref.min_price ?? 0) / 100 }}–€{{ pref.max_price / 100 }}/mo</span>
              <span v-if="pref.min_rooms">{{ pref.min_rooms }}+ rooms</span>
              <span v-if="pref.pet_friendly" class="tag">Pet friendly</span>
              <span v-if="pref.furnished" class="tag">Furnished</span>
            </div>
            <div class="pref-card__actions">
              <button @click="openEditForm(pref)" class="btn-edit">Edit</button>
              <button @click="handleDelete(pref.id)" class="btn-delete">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import type { Preference } from '../types'
import ErrorAlert from '../components/ErrorAlert.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const authStore = useAuthStore()
const userStore = useUserStore()
const router = useRouter()

const showForm = ref(false)
const editingId = ref<string | null>(null)
const saving = ref(false)

const defaultForm = () => ({
  city: '',
  country_code: 'NL',
  min_price: null as number | null,
  max_price: 1500,
  min_rooms: null as number | null,
  max_rooms: null as number | null,
  min_size_sqm: null as number | null,
  max_size_sqm: null as number | null,
  pet_friendly: false,
  furnished: null as boolean | null,
})

const form = ref(defaultForm())

onMounted(() => {
  userStore.fetchPreferences()
})

function openNewForm() {
  editingId.value = null
  form.value = defaultForm()
  showForm.value = true
}

function openEditForm(pref: Preference) {
  editingId.value = pref.id
  form.value = {
    city: pref.city,
    country_code: pref.country_code,
    min_price: pref.min_price,
    max_price: pref.max_price,
    min_rooms: pref.min_rooms,
    max_rooms: pref.max_rooms,
    min_size_sqm: pref.min_size_sqm,
    max_size_sqm: pref.max_size_sqm,
    pet_friendly: pref.pet_friendly,
    furnished: pref.furnished,
  }
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
}

async function handleSave() {
  saving.value = true
  try {
    if (editingId.value) {
      await userStore.updatePreference(editingId.value, form.value)
    } else {
      await userStore.createPreference(form.value)
    }
    cancelForm()
  } catch (e: any) {
    userStore.error = e.response?.data?.detail || 'Failed to save preference'
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: string) {
  if (!confirm('Delete this preference?')) return
  await userStore.deletePreference(id)
}

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.preferences-page { min-height: 100vh; display: flex; flex-direction: column; background: #f8f9fa; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: white; border-bottom: 1px solid #e5e7eb; }
.brand { font-size: 1.5rem; font-weight: 700; color: #4f46e5; text-decoration: none; }
.nav-links { display: flex; gap: 1.5rem; align-items: center; }
.nav-links a { color: #374151; text-decoration: none; font-size: 0.9rem; }
.nav-links a.router-link-active { color: #4f46e5; font-weight: 600; }
.btn-logout { background: none; border: 1px solid #d1d5db; color: #374151; padding: 0.375rem 0.875rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.875rem; }
.main { flex: 1; max-width: 800px; margin: 0 auto; width: 100%; padding: 2rem; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.75rem; font-weight: 700; }
.subtitle { color: #6b7280; margin-top: 0.25rem; }
.form-card { background: white; border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 2rem; border: 1px solid #e5e7eb; }
.form-card h2 { font-size: 1.125rem; font-weight: 700; margin-bottom: 1rem; }
.form { display: flex; flex-direction: column; gap: 1rem; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; }
.field label { font-size: 0.875rem; font-weight: 500; }
.field input, .field select { padding: 0.625rem 0.875rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 0.9rem; }
.checkboxes { align-items: center; }
.checkbox-label { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; cursor: pointer; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem; }
.btn-cancel { padding: 0.625rem 1.25rem; border: 1px solid #d1d5db; border-radius: 0.5rem; background: white; cursor: pointer; }
.btn-save { padding: 0.625rem 1.25rem; background: #4f46e5; color: white; border: none; border-radius: 0.5rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.list-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.list-header h2 { font-size: 1.125rem; font-weight: 700; }
.btn-add { background: #4f46e5; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; }
.loading-state { text-align: center; padding: 4rem 0; }
.empty-state { text-align: center; padding: 3rem 0; color: #6b7280; }
.pref-list { display: flex; flex-direction: column; gap: 0.75rem; }
.pref-card { background: white; border-radius: 0.75rem; padding: 1rem 1.25rem; border: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
.pref-card__info { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; font-size: 0.9rem; color: #374151; }
.pref-card__info strong { color: #111827; }
.tag { background: #eff6ff; color: #1d4ed8; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; }
.pref-card__actions { display: flex; gap: 0.5rem; }
.btn-edit { padding: 0.375rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.5rem; background: white; cursor: pointer; font-size: 0.875rem; }
.btn-delete { padding: 0.375rem 0.75rem; border: 1px solid #fca5a5; border-radius: 0.5rem; background: #fef2f2; color: #dc2626; cursor: pointer; font-size: 0.875rem; }
</style>

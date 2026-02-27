<template>
  <div class="dashboard">
    <header class="header">
      <RouterLink to="/" class="brand">Rentify</RouterLink>
      <nav class="nav-links">
        <RouterLink to="/dashboard">Dashboard</RouterLink>
        <RouterLink to="/preferences">Preferences</RouterLink>
        <button @click="handleLogout" class="btn-logout">Logout</button>
      </nav>
    </header>

    <main class="main">
      <TrialBanner v-if="authStore.user" :user="authStore.user" />

      <div class="page-header">
        <h1>Your Matches</h1>
        <p class="subtitle">Latest rental listings that match your preferences</p>
      </div>

      <div v-if="userStore.loadingMatches" class="loading-state">
        <LoadingSpinner />
      </div>

      <div v-else-if="userStore.error" class="error-state">
        <ErrorAlert :message="userStore.error" />
      </div>

      <div v-else-if="userStore.matches.length === 0" class="empty-state">
        <p>No matches yet.</p>
        <RouterLink to="/preferences" class="btn-primary">Set up preferences →</RouterLink>
      </div>

      <div v-else class="matches-grid">
        <ListingCard v-for="match in userStore.matches" :key="match.id" :match="match" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import TrialBanner from '../components/TrialBanner.vue'
import ListingCard from '../components/ListingCard.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorAlert from '../components/ErrorAlert.vue'

const authStore = useAuthStore()
const userStore = useUserStore()
const router = useRouter()

onMounted(() => {
  userStore.fetchMatches()
})

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.dashboard { min-height: 100vh; display: flex; flex-direction: column; background: #f8f9fa; }
.header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: white; border-bottom: 1px solid #e5e7eb; }
.brand { font-size: 1.5rem; font-weight: 700; color: #4f46e5; text-decoration: none; }
.nav-links { display: flex; gap: 1.5rem; align-items: center; }
.nav-links a { color: #374151; text-decoration: none; font-size: 0.9rem; }
.nav-links a.router-link-active { color: #4f46e5; font-weight: 600; }
.btn-logout { background: none; border: 1px solid #d1d5db; color: #374151; padding: 0.375rem 0.875rem; border-radius: 0.5rem; cursor: pointer; font-size: 0.875rem; }
.main { flex: 1; max-width: 960px; margin: 0 auto; width: 100%; padding: 2rem; }
.page-header { margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.75rem; font-weight: 700; }
.subtitle { color: #6b7280; margin-top: 0.25rem; }
.loading-state, .empty-state, .error-state { text-align: center; padding: 4rem 0; }
.empty-state p { color: #6b7280; margin-bottom: 1rem; }
.btn-primary { display: inline-block; background: #4f46e5; color: white; padding: 0.625rem 1.25rem; border-radius: 0.5rem; font-weight: 600; text-decoration: none; }
.matches-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
</style>

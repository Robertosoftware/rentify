<template>
  <div class="auth-page">
    <div class="auth-card">
      <RouterLink to="/" class="brand">Rentify</RouterLink>
      <h2>Welcome back</h2>
      <p class="subtitle">Sign in to your account</p>

      <ErrorAlert v-if="error" :message="error" />

      <form @submit.prevent="handleSubmit" class="form">
        <div class="field">
          <label>Email *</label>
          <input v-model="form.email" type="email" placeholder="you@example.com" required />
        </div>
        <div class="field">
          <label>Password *</label>
          <input v-model="form.password" type="password" placeholder="Your password" required />
        </div>
        <button type="submit" class="btn-submit" :disabled="authStore.loading">
          <LoadingSpinner v-if="authStore.loading" size="sm" />
          <span v-else>Sign In</span>
        </button>
      </form>

      <div class="divider"><span>or</span></div>
      <GoogleSignIn />

      <p class="footer-link">Don't have an account? <RouterLink to="/signup">Sign up</RouterLink></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ErrorAlert from '../components/ErrorAlert.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import GoogleSignIn from '../components/GoogleSignIn.vue'

const authStore = useAuthStore()
const router = useRouter()
const error = ref<string | null>(null)
const form = ref({ email: '', password: '' })

async function handleSubmit() {
  error.value = null
  try {
    await authStore.login(form.value.email, form.value.password)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Login failed. Please try again.'
  }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f8f9fa; padding: 2rem; }
.auth-card { background: white; border-radius: 1rem; padding: 2.5rem; width: 100%; max-width: 440px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
.brand { display: block; font-size: 1.5rem; font-weight: 700; color: #4f46e5; margin-bottom: 1.5rem; text-decoration: none; }
.auth-card h2 { font-size: 1.5rem; margin-bottom: 0.25rem; }
.subtitle { color: #6b7280; margin-bottom: 1.5rem; }
.form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.25rem; }
.field label { font-size: 0.875rem; font-weight: 500; }
.field input { padding: 0.625rem 0.875rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem; }
.btn-submit { width: 100%; padding: 0.75rem; background: #4f46e5; color: white; border: none; border-radius: 0.5rem; font-weight: 600; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.divider { display: flex; align-items: center; margin: 1.25rem 0; color: #9ca3af; }
.divider::before, .divider::after { content: ''; flex: 1; border-bottom: 1px solid #e5e7eb; }
.divider span { padding: 0 0.75rem; }
.footer-link { text-align: center; margin-top: 1.5rem; color: #6b7280; font-size: 0.875rem; }
</style>

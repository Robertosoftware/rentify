<template>
  <div class="auth-page">
    <div class="auth-card">
      <RouterLink to="/" class="brand">Rentify</RouterLink>
      <h2>Create your account</h2>
      <p class="subtitle">7-day free trial. No credit card required.</p>

      <ErrorAlert v-if="error" :message="error" />

      <form @submit.prevent="handleSubmit" class="form">
        <div class="field">
          <label>Full name</label>
          <input v-model="form.fullName" type="text" placeholder="Jane Doe" />
        </div>
        <div class="field">
          <label>Email *</label>
          <input v-model="form.email" type="email" placeholder="you@example.com" required />
        </div>
        <div class="field">
          <label>Password *</label>
          <input v-model="form.password" type="password" placeholder="Min. 8 characters" required minlength="8" />
        </div>
        <div class="field field--checkbox">
          <input id="gdpr" v-model="form.gdprConsent" type="checkbox" />
          <label for="gdpr">I agree to the <RouterLink to="/privacy">Privacy Policy</RouterLink> (required by GDPR)</label>
        </div>
        <div v-if="!form.gdprConsent && submitAttempted" class="form-error">
          GDPR consent is required to create an account.
        </div>
        <button type="submit" class="btn-submit" :disabled="authStore.loading">
          <LoadingSpinner v-if="authStore.loading" size="sm" />
          <span v-else>Create Account</span>
        </button>
      </form>

      <div class="divider"><span>or</span></div>
      <GoogleSignIn />

      <p class="footer-link">Already have an account? <RouterLink to="/login">Sign in</RouterLink></p>
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
const submitAttempted = ref(false)
const form = ref({ fullName: '', email: '', password: '', gdprConsent: false })

async function handleSubmit() {
  submitAttempted.value = true
  if (!form.value.gdprConsent) {
    error.value = 'GDPR consent is required to create an account.'
    return
  }
  error.value = null
  try {
    await authStore.register(form.value.email, form.value.password, form.value.fullName, form.value.gdprConsent)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Registration failed. Please try again.'
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
.field input[type="text"], .field input[type="email"], .field input[type="password"] { padding: 0.625rem 0.875rem; border: 1px solid #d1d5db; border-radius: 0.5rem; font-size: 1rem; }
.field--checkbox { flex-direction: row; align-items: flex-start; gap: 0.5rem; }
.field--checkbox input { margin-top: 0.2rem; }
.field--checkbox label { font-size: 0.875rem; font-weight: 400; }
.form-error { color: #dc2626; font-size: 0.875rem; }
.btn-submit { width: 100%; padding: 0.75rem; background: #4f46e5; color: white; border: none; border-radius: 0.5rem; font-weight: 600; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.divider { display: flex; align-items: center; margin: 1.25rem 0; color: #9ca3af; }
.divider::before, .divider::after { content: ''; flex: 1; border-bottom: 1px solid #e5e7eb; }
.divider span { padding: 0 0.75rem; }
.footer-link { text-align: center; margin-top: 1.5rem; color: #6b7280; font-size: 0.875rem; }
</style>

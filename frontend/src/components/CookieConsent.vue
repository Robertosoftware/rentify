<template>
  <Transition name="slide-up">
    <div v-if="!consented" class="cookie-banner">
      <p>We use only necessary cookies for authentication. No tracking. <RouterLink to="/privacy">Privacy Policy</RouterLink></p>
      <button @click="accept" class="btn-accept">Accept</button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'

const consented = ref(true)
onMounted(() => {
  consented.value = document.cookie.includes('rentify_cookie_consent=true')
})
function accept() {
  document.cookie = 'rentify_cookie_consent=true; max-age=31536000; path=/'
  consented.value = true
}
</script>

<style scoped>
.cookie-banner { position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%); background: #1a1a2e; color: white; padding: 1rem 1.5rem; border-radius: 0.75rem; display: flex; align-items: center; gap: 1.5rem; max-width: 600px; width: calc(100% - 3rem); box-shadow: 0 8px 32px rgba(0,0,0,0.3); z-index: 1000; }
.cookie-banner p { font-size: 0.875rem; margin: 0; }
.btn-accept { padding: 0.375rem 0.875rem; border-radius: 0.5rem; background: #4f46e5; color: white; border: none; font-weight: 600; cursor: pointer; white-space: nowrap; }
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateX(-50%) translateY(100px); opacity: 0; }
</style>

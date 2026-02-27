<template>
  <div class="not-found">
    <div class="not-found__content">
      <h1>404</h1>
      <p>Page not found.</p>
      <RouterLink to="/" class="btn-home">Go to Homepage</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.not-found { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f8f9fa; text-align: center; }
.not-found__content h1 { font-size: 6rem; font-weight: 800; color: #4f46e5; margin-bottom: 0.5rem; }
.not-found__content p { color: #6b7280; font-size: 1.25rem; margin-bottom: 2rem; }
.btn-home { display: inline-block; background: #4f46e5; color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; font-weight: 600; text-decoration: none; }
</style>

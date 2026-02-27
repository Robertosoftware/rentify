<template>
  <a :href="googleAuthUrl" class="btn-google">
    <svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
      <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
      <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
      <path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
      <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 6.29C4.672 4.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
    </svg>
    Continue with Google
  </a>
</template>

<script setup lang="ts">
const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'
const googleAuthUrl = `${API_URL}/auth/google`
</script>

<style scoped>
.btn-google { display: flex; align-items: center; justify-content: center; gap: 0.75rem; width: 100%; padding: 0.625rem 1.25rem; border: 1px solid #d1d5db; border-radius: 0.5rem; background: white; color: #374151; font-weight: 600; font-size: 1rem; cursor: pointer; text-decoration: none; transition: background 0.2s; }
.btn-google:hover { background: #f9fafb; text-decoration: none; }
</style>

<template>
  <RouterView />
  <CookieConsent />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import CookieConsent from './components/CookieConsent.vue'
</script>

<style>
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #1a1a2e;
  background: #f8f9fa;
  line-height: 1.6;
}

a {
  color: #4f46e5;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>

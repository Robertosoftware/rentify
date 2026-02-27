<template>
  <div class="spinner" :class="`spinner--${size || 'md'}`" role="status" aria-label="Loading">
    <div class="spinner__circle"></div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ size?: 'sm' | 'md' | 'lg' }>()
</script>

<style scoped>
.spinner { display: inline-flex; align-items: center; justify-content: center; }
.spinner__circle { border: 2px solid #e5e7eb; border-top-color: #4f46e5; border-radius: 50%; animation: spin 0.7s linear infinite; }
.spinner--sm .spinner__circle { width: 16px; height: 16px; }
.spinner--md .spinner__circle { width: 24px; height: 24px; }
.spinner--lg .spinner__circle { width: 40px; height: 40px; border-width: 3px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>

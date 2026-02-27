<template>
  <div class="error-alert" role="alert">
    <span>⚠️ {{ message }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ message: string }>()
</script>

<style scoped>
.error-alert { display: flex; align-items: flex-start; gap: 0.5rem; padding: 0.75rem 1rem; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 0.5rem; color: #991b1b; font-size: 0.875rem; margin-bottom: 1rem; }
</style>

<template>
  <div class="listing-card">
    <div class="listing-card__header">
      <span class="listing-card__channel">{{ match.notification_channel || 'match' }}</span>
      <span class="listing-card__score">{{ (match.score * 100).toFixed(0) }}% match</span>
    </div>
    <p class="listing-card__id">Match #{{ match.id.slice(0, 8) }}</p>
    <p class="listing-card__date">{{ formatDate(match.created_at) }}</p>
  </div>
</template>

<script setup lang="ts">
import type { Match } from '../types'
defineProps<{ match: Match }>()
function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.listing-card { background: white; border-radius: 0.75rem; padding: 1.25rem; border: 1px solid #e5e7eb; }
.listing-card__header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.listing-card__channel { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #6b7280; }
.listing-card__score { font-size: 0.875rem; font-weight: 600; color: #4f46e5; }
.listing-card__id { font-weight: 500; margin-bottom: 0.25rem; }
.listing-card__date { font-size: 0.875rem; color: #6b7280; }
</style>

<template>
  <div v-if="showBanner" class="trial-banner" :class="bannerClass">
    <span v-if="user.subscription_status === 'trialing'">
      🕐 Trial — {{ daysLeft }} days remaining.
      <a href="/billing/create-checkout-session">Upgrade to keep access →</a>
    </span>
    <span v-else-if="user.subscription_status === 'past_due'">
      ⚠️ Payment failed. <a href="/billing/create-portal-session">Update payment method →</a>
    </span>
    <span v-else-if="user.subscription_status === 'none'">
      Start your 7-day free trial to unlock all features.
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { User } from '../types'

const props = defineProps<{ user: User }>()

const showBanner = computed(() =>
  ['trialing', 'past_due', 'none'].includes(props.user.subscription_status)
)
const bannerClass = computed(() => ({
  'trial-banner--warning': props.user.subscription_status === 'past_due',
  'trial-banner--info': props.user.subscription_status === 'trialing',
}))
const daysLeft = computed(() => {
  if (!props.user.trial_ends_at) return 0
  const diff = new Date(props.user.trial_ends_at).getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
})
</script>

<style scoped>
.trial-banner { padding: 0.75rem 1.5rem; background: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 0.5rem; margin-bottom: 1.5rem; font-size: 0.9rem; }
.trial-banner--warning { background: #fff7ed; border-color: #f97316; }
</style>

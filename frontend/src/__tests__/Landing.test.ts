import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Landing from '../pages/Landing.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: Landing },
    { path: '/signup', component: { template: '<div />' } },
    { path: '/login', component: { template: '<div />' } },
    { path: '/privacy', component: { template: '<div />' } },
  ],
})

async function mountLanding() {
  await router.push('/')
  await router.isReady()
  return mount(Landing, { global: { plugins: [router] } })
}

describe('Landing page', () => {
  it('renders the brand name', async () => {
    const w = await mountLanding()
    expect(w.text()).toContain('Rentify')
  })

  it('has a "Start Free Trial" CTA button', async () => {
    const w = await mountLanding()
    expect(w.text()).toContain('Start Free Trial')
  })

  it('mentions the 7-day free trial in the hero section', async () => {
    const w = await mountLanding()
    expect(w.text()).toContain('7-day free trial')
  })

  it('has links to login and signup', async () => {
    const w = await mountLanding()
    const links = w.findAll('a')
    const hrefs = links.map((l) => l.attributes('href'))
    expect(hrefs).toContain('/login')
    expect(hrefs.some((h) => h?.includes('signup'))).toBe(true)
  })

  it('shows the four feature tiles', async () => {
    const w = await mountLanding()
    expect(w.text()).toContain('Multi-Site Search')
    expect(w.text()).toContain('Instant Notifications')
    expect(w.text()).toContain('Smart Matching')
    expect(w.text()).toContain('GDPR Compliant')
  })
})

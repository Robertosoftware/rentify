import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import Dashboard from '../pages/Dashboard.vue'

vi.mock('../composables/useApi', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: { items: [], total: 0, page: 1, per_page: 10, pages: 0 } }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/dashboard', component: Dashboard },
    { path: '/', component: { template: '<div />' } },
    { path: '/preferences', component: { template: '<div />' } },
    { path: '/login', component: { template: '<div />' } },
  ],
})

async function mountDashboard() {
  await router.push('/dashboard')
  await router.isReady()
  const pinia = createPinia()
  setActivePinia(pinia)
  return mount(Dashboard, { global: { plugins: [router, pinia] } })
}

describe('Dashboard page', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders the page heading', async () => {
    const w = await mountDashboard()
    expect(w.text()).toContain('Your Matches')
  })

  it('shows empty state message when no matches', async () => {
    const w = await mountDashboard()
    // allow async fetchMatches to settle
    await w.vm.$nextTick()
    await w.vm.$nextTick()
    expect(w.text()).toContain('No matches yet')
  })

  it('has a link to preferences', async () => {
    const w = await mountDashboard()
    const links = w.findAll('a')
    const hrefs = links.map((l) => l.attributes('href'))
    expect(hrefs.some((h) => h?.includes('preferences'))).toBe(true)
  })

  it('has a logout button', async () => {
    const w = await mountDashboard()
    expect(w.text()).toContain('Logout')
  })
})

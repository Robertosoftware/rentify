import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import Signup from '../pages/Signup.vue'

vi.mock('../composables/useApi', () => ({
  default: {
    post: vi.fn().mockResolvedValue({ data: { access_token: 'tok' } }),
    get: vi.fn().mockResolvedValue({ data: { id: '1', email: 'a@b.com', subscription_status: 'trialing' } }),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
}))

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/signup', component: Signup },
    { path: '/dashboard', component: { template: '<div />' } },
    { path: '/privacy', component: { template: '<div />' } },
    { path: '/', component: { template: '<div />' } },
  ],
})

async function mountSignup() {
  await router.push('/signup')
  await router.isReady()
  return mount(Signup, { global: { plugins: [router, createPinia()] } })
}

describe('Signup page', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders the email and password fields', async () => {
    const w = await mountSignup()
    expect(w.find('input[type="email"]').exists()).toBe(true)
    expect(w.find('input[type="password"]').exists()).toBe(true)
  })

  it('shows GDPR checkbox', async () => {
    const w = await mountSignup()
    expect(w.find('input[type="checkbox"]').exists()).toBe(true)
  })

  it('shows GDPR error when submitting without consent', async () => {
    const w = await mountSignup()
    await w.find('form').trigger('submit')
    await w.vm.$nextTick()
    expect(w.text()).toContain('GDPR consent is required')
  })

  it('has a link to the login page', async () => {
    const w = await mountSignup()
    const links = w.findAll('a')
    const hrefs = links.map((l) => l.attributes('href'))
    expect(hrefs).toContain('/login')
  })
})

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../pages/Landing.vue') },
    { path: '/signup', component: () => import('../pages/Signup.vue') },
    { path: '/login', component: () => import('../pages/Login.vue') },
    {
      path: '/dashboard',
      component: () => import('../pages/Dashboard.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/preferences',
      component: () => import('../pages/Preferences.vue'),
      meta: { requiresAuth: true },
    },
    { path: '/privacy', component: () => import('../pages/Privacy.vue') },
    { path: '/:pathMatch(.*)*', component: () => import('../pages/NotFound.vue') },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    if (!authStore.isAuthenticated) {
      await authStore.tryRefresh()
      if (!authStore.isAuthenticated) {
        return '/login'
      }
    }
  }
})

export default router

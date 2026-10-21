
import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ComponentView from '../views/ComponentView.vue'
import ProductDetailsView from '../views/ProductDetailsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    {
      path: '/components',
      name: 'components',
      component: ComponentView,
      meta: { requiresAuth: true },
    },
    {
      path: '/products/:id',
      name: 'product-details',
      component: ProductDetailsView,
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to) => {
  if (!to.matched.some((record) => record.meta.requiresAuth)) {
    return true
  }

  try {
    const response = await fetch(
        'http://localhost:8000/api/auth/me/',
        { credentials: 'include' },
    )

    if (response.ok) {
      return true
    }
  } catch (error) {
    console.error('Authentication check failed:', error)
  }

  return {
    name: 'login',
    query: { redirect: to.fullPath },
  }
})

export default router

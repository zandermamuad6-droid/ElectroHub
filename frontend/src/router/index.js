import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import ComponentView from '../views/ComponentView.vue'
import ProductDetailsView from '../views/ProductDetailsView.vue'
import CartView from '../views/CartView.vue'
import MyOrdersView from '../views/MyOrdersView.vue'
import AdminOrdersView from '../views/AdminOrdersView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

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
      path: '/register',
      name: 'register',
      component: RegisterView,
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
    {
      path: '/cart',
      name: 'cart',
      component: CartView,
      meta: { requiresAuth: true },
    },
    {
      path: '/my-orders',
      name: 'my-orders',
      component: MyOrdersView,
      meta: { requiresAuth: true },
    },
    {
      path: '/admin/orders',
      name: 'admin-orders',
      component: AdminOrdersView,
      meta: {
        requiresAuth: true,
        requiresAdmin: true,
      },
    },
  ],
})

router.beforeEach(async (to) => {
  const requiresAuth = to.matched.some(
      (record) => record.meta.requiresAuth,
  )

  // Public pages, including Login and Register.
  if (!requiresAuth) {
    return true
  }

  try {
    const response = await fetch(
        'http://localhost:8000/api/auth/me/',
        {
          method: 'GET',
          credentials: 'include',
        },
    )

    if (!response.ok) {
      return {
        name: 'login',
        query: { redirect: to.fullPath },
      }
    }

    const user = await response.json()

    // Admin-only pages.
    if (
        to.matched.some((record) => record.meta.requiresAdmin) &&
        user.is_staff !== true
    ) {
      return { name: 'dashboard' }
    }

    return true
  } catch (error) {
    console.error('Authentication check failed:', error)

    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }
})

export default router
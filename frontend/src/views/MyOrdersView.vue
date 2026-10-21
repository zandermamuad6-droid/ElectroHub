
<template>
  <div class="orders-page">
    <div class="orders-header">
      <div>
        <h1>My Orders</h1>
        <p>View and track your orders from ElectroHub.</p>
        <p class="refresh-note">
          Order status refreshes automatically every 10 seconds.
        </p>
      </div>

      <button @click="loadOrders" :disabled="loading">
        {{ loading ? 'Loading...' : 'Refresh Orders' }}
      </button>
    </div>

    <p v-if="loading && orders.length === 0" class="message">
      Loading your orders...
    </p>

    <div v-else-if="error && orders.length === 0" class="error">
      {{ error }}
      <button @click="loadOrders">Try Again</button>
    </div>

    <div v-else-if="orders.length === 0" class="empty">
      <h2>No orders yet</h2>
      <p>Your checkout orders will appear here.</p>
      <RouterLink to="/components">Browse Components</RouterLink>
    </div>

    <div v-else class="orders-list">
      <p v-if="error" class="inline-error">{{ error }}</p>

      <article
          v-for="order in orders"
          :key="order.id"
          class="order-card"
      >
        <div class="order-top">
          <div>
            <h2>{{ order.order_number }}</h2>
            <p>{{ formatDate(order.created_at) }}</p>
          </div>

          <span
              class="status"
              :class="statusClass(order.status)"
          >
            {{ formatStatus(order.status) }}
          </span>
        </div>

        <div class="tracking">
          <strong>Order tracking</strong>
          <p>{{ statusMessage(order.status) }}</p>
        </div>

        <div class="order-items">
          <div
              v-for="(item, index) in order.items"
              :key="`${order.id}-${index}`"
              class="item-row"
          >
            <div>
              <strong>{{ item.component_name }}</strong>
              <p>Quantity: {{ item.quantity }}</p>
            </div>

            <span>{{ money(item.subtotal) }}</span>
          </div>
        </div>

        <div class="order-bottom">
          <div>
            <p>
              Payment:
              <strong>
                {{ (order.payment_method || 'N/A').toUpperCase() }}
              </strong>
            </p>

            <p>
              Payment status:
              <strong>{{ formatStatus(order.payment_status) }}</strong>
            </p>
          </div>

          <div class="total">
            <span>Total</span>
            <strong>{{ money(order.total_amount) }}</strong>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getMyOrders } from '../services/api.js'

const orders = ref([])
const loading = ref(false)
const error = ref('')
let refreshTimer = null

async function loadOrders() {
  if (loading.value) return

  loading.value = true
  error.value = ''

  try {
    const response = await getMyOrders()

    orders.value = Array.isArray(response)
        ? response
        : Array.isArray(response.results)
            ? response.results
            : []
  } catch (err) {
    error.value = err.message || 'Failed to load your orders.'
  } finally {
    loading.value = false
  }
}

function formatStatus(status) {
  if (!status) return 'Unknown'
  return String(status)
      .replaceAll('_', ' ')
      .replace(/\b\w/g, letter => letter.toUpperCase())
}

function statusClass(status) {
  const value = String(status || '').toLowerCase()

  if (value === 'completed' || value === 'delivered') {
    return 'status-completed'
  }

  if (value === 'processing' || value === 'shipped') {
    return 'status-processing'
  }

  if (value === 'cancelled' || value === 'canceled') {
    return 'status-cancelled'
  }

  return 'status-pending'
}

function statusMessage(status) {
  const value = String(status || '').toLowerCase()

  if (value === 'pending') {
    return 'Your order has been received and is waiting for processing.'
  }

  if (value === 'processing') {
    return 'Your order is being prepared by ElectroHub.'
  }

  if (value === 'shipped') {
    return 'Your order has been shipped.'
  }

  if (value === 'completed' || value === 'delivered') {
    return 'Your order has been completed. Thank you for shopping with us!'
  }

  if (value === 'cancelled' || value === 'canceled') {
    return 'This order has been cancelled.'
  }

  return 'Check the status above for the latest order information.'
}

function money(value) {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(Number(value) || 0)
}

function formatDate(value) {
  if (!value) return 'Date unavailable'

  return new Date(value).toLocaleString('en-PH', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

onMounted(() => {
  loadOrders()

  refreshTimer = setInterval(() => {
    loadOrders()
  }, 10000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.orders-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 24px;
  color: #1f2937;
}

.orders-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 28px;
}

.orders-header h1 {
  margin: 0 0 8px;
  font-size: 30px;
}

.orders-header p,
.order-top p,
.item-row p {
  margin: 0;
  color: #6b7280;
}

.refresh-note {
  margin-top: 8px !important;
  font-size: 13px;
}

button {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: white;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.order-card {
  margin-bottom: 20px;
  padding: 24px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: white;
}

.order-top,
.item-row,
.order-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.order-top {
  padding-bottom: 18px;
  border-bottom: 1px solid #e5e7eb;
}

.order-top h2 {
  margin: 0 0 6px;
  font-size: 18px;
}

.status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  text-transform: capitalize;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-processing {
  background: #dbeafe;
  color: #1d4ed8;
}

.status-completed {
  background: #dcfce7;
  color: #166534;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.tracking {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 8px;
  background: #f9fafb;
}

.tracking p {
  margin: 6px 0 0;
  color: #4b5563;
  font-size: 14px;
}

.item-row {
  padding: 16px 0;
  border-bottom: 1px solid #f3f4f6;
}

.item-row p {
  margin-top: 5px;
  font-size: 14px;
}

.order-bottom {
  padding-top: 18px;
}

.order-bottom p {
  margin: 5px 0;
  font-size: 14px;
}

.total {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.total strong {
  font-size: 22px;
}

.empty,
.message,
.error {
  padding: 32px;
  border-radius: 12px;
  background: #f9fafb;
  text-align: center;
}

.empty a {
  display: inline-block;
  margin-top: 12px;
  color: #2563eb;
}

.error,
.inline-error {
  color: #b91c1c;
}

.error button {
  display: block;
  margin: 16px auto 0;
}

.inline-error {
  margin-bottom: 16px;
}

@media (max-width: 600px) {
  .orders-page {
    padding: 20px 12px;
  }

  .orders-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .order-card {
    padding: 16px;
  }

  .order-bottom {
    align-items: flex-start;
    flex-direction: column;
  }

  .total {
    align-items: flex-start;
  }
}
</style>

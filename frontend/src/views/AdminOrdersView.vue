```vue
<template>
  <main class="admin-page">
    <header class="page-header">
      <div>
        <p class="eyebrow">ELECTROHUB ADMIN</p>
        <h1>Order Management</h1>
        <p class="subtitle">
          View customer orders and update their status.
        </p>
      </div>

      <button
          class="button button-primary"
          type="button"
          :disabled="loading"
          @click="loadOrders"
      >
        {{ loading ? "Loading..." : "Refresh Orders" }}
      </button>
    </header>

    <div v-if="errorMessage" class="message error" role="alert">
      {{ errorMessage }}
    </div>

    <div v-if="successMessage" class="message success" role="status">
      {{ successMessage }}
    </div>

    <section class="summary-grid">
      <article class="summary-card">
        <span class="summary-label">Total Orders</span>
        <strong>{{ orders.length }}</strong>
      </article>

      <article class="summary-card">
        <span class="summary-label">Pending Orders</span>
        <strong>{{ pendingCount }}</strong>
      </article>

      <article class="summary-card">
        <span class="summary-label">Completed Orders</span>
        <strong>{{ completedCount }}</strong>
      </article>
    </section>

    <section class="orders-card">
      <div class="table-heading">
        <h2>Customer Orders</h2>
        <span>{{ orders.length }} order(s)</span>
      </div>

      <div v-if="loading && orders.length === 0" class="empty-state">
        Loading orders...
      </div>

      <div v-else-if="orders.length === 0" class="empty-state">
        No orders found.
      </div>

      <div v-else class="table-wrapper">
        <table>
          <thead>
          <tr>
            <th>Order</th>
            <th>Customer</th>
            <th>Date</th>
            <th>Items</th>
            <th>Total</th>
            <th>Payment</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
          </thead>

          <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>
              <strong class="order-number">
                {{ order.order_number }}
              </strong>
            </td>

            <td class="customer-name">
              {{ order.customer || "N/A" }}
            </td>

            <td class="date-cell">
              {{ formatDate(order.created_at) }}
            </td>

            <td>
              <details class="items-details">
                <summary>
                  {{ (order.items || []).length }} item(s)
                </summary>

                <ul class="item-list">
                  <li
                      v-for="(item, index) in order.items || []"
                      :key="`${order.id}-${index}`"
                  >
                    <strong>{{ item.component_name }}</strong>
                    <span>
                        Qty: {{ item.quantity }} ·
                        {{ formatCurrency(item.subtotal) }}
                      </span>
                  </li>
                </ul>
              </details>
            </td>

            <td class="amount">
              {{ formatCurrency(order.total_amount) }}
            </td>

            <td>
                <span class="payment-method">
                  {{ order.payment_method || "N/A" }}
                </span>
              <span class="payment-status">
                  {{ order.payment_status || "N/A" }}
                </span>
            </td>

            <td>
              <select
                  v-model="selectedStatuses[order.id]"
                  class="status-select"
                  :class="`status-${selectedStatuses[order.id]}`"
                  :disabled="savingId === order.id"
                  :aria-label="`Status for ${order.order_number}`"
              >
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </td>

            <td>
              <button
                  class="button button-update"
                  type="button"
                  :disabled="
                    savingId === order.id ||
                    selectedStatuses[order.id] === order.status
                  "
                  @click="saveStatus(order)"
              >
                {{
                  savingId === order.id ? "Saving..." : "Update"
                }}
              </button>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </section>

    <button
        class="button button-back"
        type="button"
        @click="$router.push('/dashboard')"
    >
      ← Back to Dashboard
    </button>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  getAdminOrders,
  updateAdminOrderStatus,
} from "../services/api";

const orders = ref([]);
const selectedStatuses = ref({});
const loading = ref(false);
const savingId = ref(null);
const errorMessage = ref("");
const successMessage = ref("");

const pendingCount = computed(() =>
    orders.value.filter((order) => order.status === "pending").length
);

const completedCount = computed(() =>
    orders.value.filter((order) => order.status === "completed").length
);

function formatCurrency(value) {
  const amount = Number(value ?? 0);

  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
  }).format(amount);
}

function formatDate(value) {
  if (!value) return "N/A";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "N/A";

  return date.toLocaleString("en-PH", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

async function loadOrders() {
  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const result = await getAdminOrders();

    orders.value = Array.isArray(result) ? result : [];

    selectedStatuses.value = Object.fromEntries(
        orders.value.map((order) => [order.id, order.status])
    );
  } catch (error) {
    errorMessage.value = error.message || "Unable to load orders.";
  } finally {
    loading.value = false;
  }
}

async function saveStatus(order) {
  const newStatus = selectedStatuses.value[order.id];

  if (!newStatus || newStatus === order.status) return;

  savingId.value = order.id;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    await updateAdminOrderStatus(order.id, newStatus);

    order.status = newStatus;

    successMessage.value =
        `Order ${order.order_number} updated to ${newStatus}.`;
  } catch (error) {
    selectedStatuses.value[order.id] = order.status;

    errorMessage.value =
        error.message || "Unable to update order status.";
  } finally {
    savingId.value = null;
  }
}

onMounted(loadOrders);
</script>

<style scoped>
.admin-page {
  box-sizing: border-box;
  min-height: 100vh;
  padding: 32px;
  background: #f1f5f9 !important;
  color: #172033 !important;
  font-family: Arial, Helvetica, sans-serif;
}

.admin-page * {
  box-sizing: border-box;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #1d4ed8 !important;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 2px;
}

.admin-page h1 {
  margin: 0 0 10px;
  color: #111827 !important;
  font-size: 32px;
  font-weight: 800;
}

.subtitle {
  margin: 0;
  color: #475569 !important;
  font-size: 16px;
  line-height: 1.6;
}

.button {
  border: 0;
  border-radius: 8px;
  padding: 11px 16px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.button:focus-visible,
.status-select:focus-visible {
  outline: 3px solid #93c5fd;
  outline-offset: 2px;
}

.button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.button-primary {
  background: #1d4ed8;
  color: #ffffff !important;
}

.button-primary:hover:not(:disabled) {
  background: #1e40af;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-bottom: 24px;
}

.summary-card,
.orders-card {
  background: #ffffff !important;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 14px rgb(15 23 42 / 5%);
}

.summary-card {
  padding: 22px;
}

.summary-label {
  display: block;
  color: #475569 !important;
  font-size: 14px;
  font-weight: 600;
}

.summary-card strong {
  display: block;
  margin-top: 10px;
  color: #0f172a !important;
  font-size: 30px;
  font-weight: 800;
}

.orders-card {
  padding: 20px;
}

.table-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.table-heading h2 {
  margin: 0;
  color: #111827 !important;
  font-size: 19px;
  font-weight: 800;
}

.table-heading > span {
  color: #475569 !important;
  font-size: 13px;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

thead th {
  padding: 15px 12px;
  background: #eaf0f8 !important;
  border-bottom: 1px solid #cbd5e1;
  color: #334155 !important;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  white-space: nowrap;
}

tbody td {
  padding: 16px 12px;
  border-bottom: 1px solid #e2e8f0;
  color: #334155 !important;
  font-size: 14px;
  vertical-align: middle;
}

tbody tr:hover {
  background: #f8fafc;
}

.order-number {
  color: #1d4ed8 !important;
  font-weight: 800;
  white-space: nowrap;
}

.customer-name {
  color: #1e293b !important;
  font-weight: 600;
}

.date-cell {
  min-width: 155px;
  white-space: nowrap;
}

.amount {
  color: #0f172a !important;
  font-weight: 800;
  white-space: nowrap;
}

.payment-method,
.payment-status {
  display: block;
  color: #334155 !important;
  text-transform: capitalize;
}

.payment-method {
  font-weight: 700;
}

.payment-status {
  margin-top: 5px;
  color: #64748b !important;
  font-size: 12px;
}

.status-select {
  min-width: 130px;
  padding: 10px 28px 10px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 7px;
  background-color: #ffffff !important;
  color: #172033 !important;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.status-select option {
  background: #ffffff;
  color: #172033;
}

.status-pending {
  border-color: #fbbf24;
}

.status-processing {
  border-color: #60a5fa;
}

.status-completed {
  border-color: #4ade80;
}

.status-cancelled {
  border-color: #f87171;
}

.button-update {
  background: #1d4ed8;
  color: #ffffff !important;
  white-space: nowrap;
}

.button-update:hover:not(:disabled) {
  background: #1e40af;
}

.button-back {
  margin-top: 22px;
  background: #e2e8f0;
  color: #172033 !important;
}

.button-back:hover {
  background: #cbd5e1;
}

.items-details summary {
  color: #1d4ed8 !important;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}

.item-list {
  min-width: 200px;
  padding-left: 18px;
  color: #334155 !important;
}

.item-list li {
  margin-top: 10px;
  line-height: 1.5;
}

.item-list li strong,
.item-list li span {
  display: block;
  color: #334155 !important;
}

.item-list li span {
  color: #64748b !important;
  font-size: 12px;
}

.empty-state {
  padding: 36px 20px;
  color: #475569 !important;
  text-align: center;
}

.message {
  padding: 13px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-weight: 600;
}

.error {
  background: #fee2e2;
  color: #991b1b !important;
  border: 1px solid #fecaca;
}

.success {
  background: #dcfce7;
  color: #166534 !important;
  border: 1px solid #bbf7d0;
}

@media (max-width: 900px) {
  .admin-page {
    padding: 22px;
  }

  .summary-grid {
    gap: 12px;
  }

  .summary-card {
    padding: 18px;
  }
}

@media (max-width: 650px) {
  .admin-page {
    padding: 16px;
  }

  .page-header {
    align-items: stretch;
    flex-direction: column;
  }

  .page-header .button-primary {
    align-self: flex-start;
  }

  .admin-page h1 {
    font-size: 26px;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .orders-card {
    padding: 12px;
  }

  .table-heading {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
```
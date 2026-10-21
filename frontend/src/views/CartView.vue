
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getCartItems,
  removeCartItem,
  getCurrentUser,
  checkoutCart,
} from '../services/api'

const router = useRouter()

const cartItems = ref([])
const loading = ref(true)
const removingId = ref(null)
const checkingOut = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const lastOrder = ref(null)

const cartTotal = computed(() =>
    cartItems.value.reduce(
        (total, item) => total + Number(item.subtotal || 0),
        0,
    ),
)

const totalQuantity = computed(() =>
    cartItems.value.reduce(
        (total, item) => total + Number(item.quantity || 0),
        0,
    ),
)

function formatPrice(value) {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(Number(value) || 0)
}

async function loadCart() {
  loading.value = true
  errorMessage.value = ''

  try {
    const data = await getCartItems()

    cartItems.value = Array.isArray(data)
        ? data
        : data?.results || []
  } catch (error) {
    errorMessage.value =
        error.message || 'Unable to load your cart.'
  } finally {
    loading.value = false
  }
}

async function handleRemove(item) {
  const confirmed = window.confirm(
      `Remove ${item.component_name} from your cart?`,
  )

  if (!confirmed) return

  removingId.value = item.id
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await removeCartItem(item.id)

    cartItems.value = cartItems.value.filter(
        cartItem => cartItem.id !== item.id,
    )

    successMessage.value =
        `${item.component_name} was removed from your cart.`
  } catch (error) {
    errorMessage.value =
        error.message || 'Unable to remove this item.'
  } finally {
    removingId.value = null
  }
}

async function handleCheckout() {
  if (
      checkingOut.value ||
      loading.value ||
      cartItems.value.length === 0
  ) {
    return
  }

  const confirmed = window.confirm(
      `Place your Cash on Delivery order for ${formatPrice(cartTotal.value)}?`,
  )

  if (!confirmed) return

  checkingOut.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const result = await checkoutCart('cod')

    if (!result?.order) {
      throw new Error(
          'The server response did not contain order details.',
      )
    }

    lastOrder.value = result.order
    cartItems.value = []

    successMessage.value =
        result.message || 'Your order was placed successfully.'
  } catch (error) {
    errorMessage.value =
        error.message || 'Unable to complete checkout. Please try again.'

    // Reload the cart to reflect the latest server state.
    try {
      const data = await getCartItems()
      cartItems.value = Array.isArray(data)
          ? data
          : data?.results || []
    } catch {
      // Preserve the original checkout error.
    }
  } finally {
    checkingOut.value = false
  }
}

async function initializeCart() {
  try {
    await getCurrentUser()
  } catch {
    loading.value = false

    await router.replace({
      name: 'login',
      query: { redirect: '/cart' },
    })

    return
  }

  await loadCart()
}

onMounted(initializeCart)
</script>

<template>
  <main class="cart-page">
    <div class="cart-container">
      <button
          type="button"
          class="back-button"
          @click="router.push('/')"
      >
        <span aria-hidden="true">←</span>
        Back to Home
      </button>

      <header class="page-header">
        <p class="eyebrow">ELECTROHUB</p>
        <h1>Shopping Cart</h1>
        <p>Review your electronic components before checkout.</p>
      </header>

      <div
          v-if="errorMessage"
          class="message error-message"
          role="alert"
      >
        {{ errorMessage }}
      </div>

      <div
          v-if="successMessage"
          class="message success-message"
          role="status"
      >
        {{ successMessage }}
      </div>

      <section
          v-if="loading"
          class="state-card"
          role="status"
      >
        <div class="loading-spinner"></div>
        <p>Loading your cart...</p>
      </section>

      <section
          v-else-if="lastOrder"
          class="order-confirmation"
          aria-live="polite"
      >
        <div class="confirmation-icon">✓</div>

        <p class="eyebrow">ORDER CONFIRMED</p>
        <h2>Thank you for your order!</h2>
        <p class="confirmation-description">
          Your order has been recorded successfully.
          Pay in cash when your order is delivered.
        </p>

        <div class="order-details">
          <div class="summary-row">
            <span>Order number</span>
            <strong>{{ lastOrder.order_number }}</strong>
          </div>

          <div class="summary-row">
            <span>Order status</span>
            <strong class="status-value">
              {{ lastOrder.status }}
            </strong>
          </div>

          <div class="summary-row">
            <span>Payment method</span>
            <strong>Cash on Delivery</strong>
          </div>

          <div class="summary-row total-row">
            <span>Order total</span>
            <strong>
              {{ formatPrice(lastOrder.total_amount) }}
            </strong>
          </div>
        </div>

        <h3 class="ordered-items-title">Items ordered</h3>

        <ul class="ordered-items">
          <li
              v-for="(item, index) in lastOrder.items"
              :key="`${item.component_name}-${index}`"
          >
            <span>
              {{ item.component_name }} × {{ item.quantity }}
            </span>
            <strong>{{ formatPrice(item.subtotal) }}</strong>
          </li>
        </ul>

        <button
            type="button"
            class="primary-button"
            @click="router.push('/components')"
        >
          Continue Shopping
        </button>

        <button
            type="button"
            class="continue-button"
            @click="router.push('/')"
        >
          Back to Home
        </button>
      </section>

      <section
          v-else-if="cartItems.length === 0"
          class="state-card empty-cart"
      >
        <div class="empty-icon" aria-hidden="true">🛒</div>
        <h2>Your cart is empty</h2>
        <p>Browse our inventory and add components to your cart.</p>

        <button
            type="button"
            class="primary-button"
            @click="router.push('/components')"
        >
          Browse Inventory
        </button>
      </section>

      <template v-else>
        <section class="cart-list" aria-label="Cart items">
          <article
              v-for="item in cartItems"
              :key="item.id"
              class="cart-item"
          >
            <div class="product-image">
              <img
                  v-if="item.component_image"
                  :src="item.component_image"
                  :alt="item.component_name"
                  @error="$event.target.style.display = 'none'"
              />

              <span
                  v-else
                  class="image-placeholder"
                  aria-hidden="true"
              >
                ⚡
              </span>
            </div>

            <div class="product-info">
              <p class="product-label">ELECTRONIC COMPONENT</p>
              <h2>{{ item.component_name }}</h2>
              <p class="item-id">
                Component ID: #{{ item.component }}
              </p>

              <p class="unit-price">
                {{ formatPrice(item.price) }}
                <span>per item</span>
              </p>

              <p class="quantity">
                Quantity: {{ item.quantity }}
              </p>
            </div>

            <div class="item-summary">
              <p class="subtotal-label">Subtotal</p>
              <strong>{{ formatPrice(item.subtotal) }}</strong>

              <button
                  type="button"
                  class="remove-button"
                  :disabled="removingId === item.id || checkingOut"
                  @click="handleRemove(item)"
              >
                {{
                  removingId === item.id
                      ? 'Removing...'
                      : 'Remove'
                }}
              </button>
            </div>
          </article>
        </section>

        <section class="cart-summary">
          <h2>Order Summary</h2>

          <div class="summary-row">
            <span>Different products</span>
            <strong>{{ cartItems.length }}</strong>
          </div>

          <div class="summary-row">
            <span>Total quantity</span>
            <strong>{{ totalQuantity }}</strong>
          </div>

          <div class="summary-row total-row">
            <span>Estimated total</span>
            <strong>{{ formatPrice(cartTotal) }}</strong>
          </div>

          <div class="payment-info">
            <span class="payment-icon">💵</span>
            <div>
              <strong>Cash on Delivery</strong>
              <p>Pay when your order arrives.</p>
            </div>
          </div>

          <p class="checkout-note">
            The server will validate stock and calculate the final
            item prices when you place your order.
          </p>

          <button
              type="button"
              class="primary-button checkout-button"
              :disabled="
              checkingOut ||
              loading ||
              cartItems.length === 0 ||
              removingId !== null
            "
              @click="handleCheckout"
          >
            {{
              checkingOut
                  ? 'Processing Order...'
                  : 'Place Order (COD)'
            }}
          </button>

          <button
              type="button"
              class="continue-button"
              :disabled="checkingOut"
              @click="router.push('/components')"
          >
            Continue Shopping
          </button>
        </section>
      </template>
    </div>
  </main>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.cart-page {
  min-height: 100vh;
  padding: 38px 24px 70px;
  background: #f7f5fc;
  color: #211936;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.cart-container {
  max-width: 1100px;
  margin: 0 auto;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 30px;
  padding: 8px 0;
  border: 0;
  background: transparent;
  color: #6741d9;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.page-header {
  margin-bottom: 30px;
}

.eyebrow,
.product-label {
  color: #7046dc;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 2px;
}

.page-header h1 {
  margin: 8px 0;
  font-size: clamp(30px, 5vw, 42px);
}

.page-header > p:last-child {
  color: #756d86;
  line-height: 1.7;
}

.cart-list,
.state-card,
.cart-summary,
.order-confirmation {
  border: 1px solid #e9e2f6;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 12px 36px rgb(39 20 80 / 5%);
}

.cart-list {
  overflow: hidden;
}

.cart-item {
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr) auto;
  gap: 24px;
  align-items: center;
  padding: 26px;
  border-bottom: 1px solid #eee9f6;
}

.cart-item:last-child {
  border-bottom: 0;
}

.product-image {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 140px;
  height: 140px;
  overflow: hidden;
  border-radius: 14px;
  background: #f0eaff;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.image-placeholder {
  color: #f28a55;
  font-size: 42px;
}

.product-label {
  margin: 0 0 8px;
  letter-spacing: 1px;
}

.product-info h2 {
  margin: 0 0 8px;
  font-size: 23px;
  overflow-wrap: anywhere;
}

.item-id,
.unit-price,
.quantity {
  color: #766e87;
  font-size: 14px;
}

.unit-price span {
  font-size: 13px;
}

.item-summary {
  display: flex;
  min-width: 135px;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.subtotal-label {
  margin: 0;
  color: #766e87;
  font-size: 14px;
}

.item-summary strong {
  color: #6840d6;
  font-size: 21px;
}

.remove-button {
  padding: 5px 0;
  border: 0;
  background: transparent;
  color: #c43d54;
  font: inherit;
  font-size: 14px;
  cursor: pointer;
}

.remove-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cart-summary {
  max-width: 450px;
  margin: 24px 0 0 auto;
  padding: 26px;
}

.cart-summary h2 {
  margin: 0 0 22px;
  font-size: 21px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 18px;
  color: #766e87;
}

.summary-row strong {
  color: #211936;
  text-align: right;
  overflow-wrap: anywhere;
}

.total-row {
  padding-top: 18px;
  border-top: 1px solid #eee9f6;
  color: #211936;
  font-weight: 700;
}

.total-row strong {
  color: #6840d6;
  font-size: 26px;
}

.payment-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 18px 0;
  padding: 14px;
  border: 1px solid #e9e2f6;
  border-radius: 12px;
  background: #faf8ff;
}

.payment-icon {
  font-size: 25px;
}

.payment-info strong {
  display: block;
  margin-bottom: 4px;
  color: #342353;
}

.payment-info p {
  margin: 0;
  color: #837b92;
  font-size: 13px;
}

.checkout-note {
  color: #837b92;
  font-size: 12px;
  line-height: 1.6;
}

.primary-button,
.continue-button {
  display: block;
  width: 100%;
  min-height: 48px;
  padding: 12px 18px;
  border-radius: 10px;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, opacity 0.2s ease;
}

.primary-button {
  border: 1px solid #7046dc;
  background: #7046dc;
  color: white;
}

.primary-button:hover:not(:disabled) {
  background: #5d36c6;
}

.primary-button:disabled,
.continue-button:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.checkout-button {
  margin-top: 18px;
}

.continue-button {
  margin-top: 12px;
  border: 1px solid #ded2fa;
  background: #fff;
  color: #6840d6;
}

.continue-button:hover:not(:disabled) {
  background: #f7f3ff;
}

.state-card {
  padding: 50px 24px;
  text-align: center;
}

.empty-icon {
  font-size: 44px;
}

.empty-cart h2 {
  margin-bottom: 8px;
}

.empty-cart p {
  margin-bottom: 24px;
  color: #766e87;
}

.empty-cart .primary-button {
  max-width: 260px;
  margin: 0 auto;
}

.message {
  margin-bottom: 18px;
  padding: 13px 16px;
  border-radius: 10px;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.error-message {
  border: 1px solid #f2c5cb;
  background: #fff1f2;
  color: #a52a3d;
}

.success-message {
  border: 1px solid #bce8ce;
  background: #effbf4;
  color: #167846;
}

.order-confirmation {
  max-width: 650px;
  margin: 0 auto;
  padding: 32px;
}

.confirmation-icon {
  display: grid;
  width: 58px;
  height: 58px;
  place-items: center;
  margin-bottom: 22px;
  border-radius: 50%;
  background: #e8f8ee;
  color: #16814a;
  font-size: 32px;
  font-weight: 800;
}

.order-confirmation h2 {
  margin: 8px 0;
  font-size: clamp(24px, 4vw, 32px);
}

.confirmation-description {
  color: #756d86;
  line-height: 1.7;
}

.order-details {
  margin: 26px 0;
  padding: 20px;
  border: 1px solid #eee9f6;
  border-radius: 12px;
  background: #fcfbff;
}

.order-details .summary-row:last-child {
  margin-bottom: 0;
}

.status-value {
  text-transform: capitalize;
}

.ordered-items-title {
  margin: 26px 0 12px;
}

.ordered-items {
  margin: 0 0 26px;
  padding: 0;
  list-style: none;
}

.ordered-items li {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #eee9f6;
  color: #756d86;
}

.ordered-items li strong {
  flex-shrink: 0;
  color: #342353;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  margin: 0 auto;
  border: 3px solid #e4daf9;
  border-top-color: #7046dc;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 700px) {
  .cart-page {
    padding: 24px 14px 48px;
  }

  .cart-item {
    grid-template-columns: 88px minmax(0, 1fr);
    gap: 15px;
    padding: 18px;
  }

  .product-image {
    width: 88px;
    height: 88px;
  }

  .product-info h2 {
    font-size: 19px;
  }

  .item-summary {
    grid-column: 2;
    align-items: flex-start;
    min-width: 0;
  }

  .item-summary strong {
    font-size: 19px;
  }

  .cart-summary {
    padding: 20px;
  }

  .order-confirmation {
    padding: 22px;
  }

  .order-details {
    padding: 15px;
  }

  .ordered-items li {
    flex-wrap: wrap;
  }
}
</style>

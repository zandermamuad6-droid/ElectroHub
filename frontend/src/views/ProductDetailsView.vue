
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getComponents, getCurrentUser, addToCart, getCartItems } from '../services/api'

const route = useRoute()
const router = useRouter()

const product = ref(null)
const loading = ref(true)
const error = ref('')
const imageError = ref(false)
const isAuthenticated = ref(false)
const authChecking = ref(true)
const quantity = ref(1)
const addingToCart = ref(false)
const cartMessage = ref('')
const cartError = ref('')
const cartItemCount = ref(0)
const cartCountLoading = ref(false)

const availableStock = computed(() =>
    Math.max(0, Number(product.value?.quantity) || 0),
)

const subtotal = computed(() =>
    (Number(product.value?.price) || 0) * quantity.value,
)

const productImage = computed(() => {
  const image = product.value?.image_url
  return image && !imageError.value ? image : null
})

const canAddToCart = computed(() =>
    isAuthenticated.value &&
    !authChecking.value &&
    !addingToCart.value &&
    availableStock.value > 0 &&
    Number.isInteger(quantity.value) &&
    quantity.value >= 1 &&
    quantity.value <= availableStock.value,
)

function formatPrice(price) {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(Number(price) || 0)
}

function handleImageError() {
  imageError.value = true
}

function decreaseQuantity() {
  if (quantity.value > 1) {
    quantity.value -= 1
    clearCartMessages()
  }
}

function increaseQuantity() {
  if (quantity.value < availableStock.value) {
    quantity.value += 1
    clearCartMessages()
  }
}

function updateQuantity(event) {
  const rawValue = event.target.value
  const value = Number(rawValue)

  if (
      rawValue.trim() === '' ||
      !Number.isInteger(value) ||
      value < 1
  ) {
    quantity.value = 1
  } else {
    quantity.value = Math.min(value, availableStock.value)
  }

  clearCartMessages()
}

function clearCartMessages() {
  cartMessage.value = ''
  cartError.value = ''
}

async function loadCartCount() {
  if (!isAuthenticated.value) {
    cartItemCount.value = 0
    return
  }

  cartCountLoading.value = true
  try {
    const data = await getCartItems()
    const items = Array.isArray(data) ? data : data?.results || []
    cartItemCount.value = items.reduce(
        (total, item) => total + (Number(item.quantity) || 0),
        0,
    )
  } catch {
    // Keep the product page usable if cart count cannot be loaded.
  } finally {
    cartCountLoading.value = false
  }
}

async function checkAuthentication() {
  authChecking.value = true

  try {
    await getCurrentUser()
    isAuthenticated.value = true
  } catch {
    isAuthenticated.value = false
  } finally {
    authChecking.value = false
    await loadCartCount()
  }
}

async function loadProduct() {
  loading.value = true
  error.value = ''
  product.value = null
  imageError.value = false
  quantity.value = 1
  clearCartMessages()

  try {
    const data = await getComponents()
    const products = Array.isArray(data)
        ? data
        : data?.results || []

    const productId = Number(route.params.id)

    if (!Number.isInteger(productId) || productId < 1) {
      error.value = 'Invalid product ID.'
      return
    }

    product.value = products.find(
        item => Number(item.id) === productId,
    ) || null

    if (!product.value) {
      error.value = 'Product not found or no longer available.'
    }
  } catch (err) {
    error.value = err.message || 'Unable to load product details.'
  } finally {
    loading.value = false
  }
}

async function handleAddToCart() {
  if (!product.value) return

  if (!isAuthenticated.value) {
    await router.push({
      name: 'login',
      query: { redirect: route.fullPath },
    })
    return
  }

  if (!canAddToCart.value) {
    cartError.value = availableStock.value <= 0
        ? 'This product is currently out of stock.'
        : 'Please choose a valid quantity within the available stock.'
    return
  }

  addingToCart.value = true
  clearCartMessages()

  try {
    const result = await addToCart(product.value.id, quantity.value)

    cartMessage.value =
        `${product.value.name} added to your cart successfully.`
    await loadCartCount()

    // Refresh product data so the page can reflect any stock changes.
    // Cart addition does not itself reserve inventory.
    if (result?.id) {
      quantity.value = 1
    }
  } catch (err) {
    cartError.value =
        err.message || 'Unable to add this product to your cart.'
  } finally {
    addingToCart.value = false
  }
}

function goToLogin() {
  router.push({
    name: 'login',
    query: { redirect: route.fullPath },
  })
}

onMounted(async () => {
  await Promise.all([
    checkAuthentication(),
    loadProduct(),
  ])
})

// Support navigating directly from one product to another.
watch(
    () => route.params.id,
    async (newId, oldId) => {
      if (newId !== oldId) {
        await loadProduct()
      }
    },
)
</script>

<template>
  <main class="details-page">
    <div class="page-container">
      <div class="top-navigation">
        <button
            type="button"
            class="back-button"
            @click="router.push('/')"
        >
          <span aria-hidden="true">←</span>
          Back to Home
        </button>

        <button
            type="button"
            class="cart-navigation-button"
            aria-label="Open shopping cart"
            @click="router.push('/cart')"
        >
          <span class="cart-icon" aria-hidden="true">🛒</span>
          <span>Cart</span>
          <span v-if="cartItemCount > 0" class="cart-count">
            {{ cartItemCount }}
          </span>
          <span v-else-if="cartCountLoading" class="cart-count">…</span>
        </button>
      </div>

      <div v-if="loading" class="message-card" role="status">
        <div class="loading-spinner"></div>
        <h2>Loading product details</h2>
        <p>Please wait while we retrieve the product information.</p>
      </div>

      <section v-else-if="error" class="message-card">
        <div class="message-icon" aria-hidden="true">!</div>
        <h2>Product unavailable</h2>
        <p class="error-message">{{ error }}</p>
        <button
            type="button"
            class="primary-button"
            @click="loadProduct"
        >
          Try Again
        </button>
        <button
            type="button"
            class="secondary-button"
            @click="router.push('/')"
        >
          Browse Products
        </button>
      </section>

      <section v-else-if="product" class="product-card">
        <div class="product-visual">
          <div class="image-label">PRODUCT PREVIEW</div>

          <div class="product-image">
            <img
                v-if="productImage"
                :key="productImage"
                :src="productImage"
                :alt="product.name || 'Electronic component'"
                class="product-photo"
                @error="handleImageError"
            />

            <div
                v-else
                class="product-icon"
                role="img"
                aria-label="No product image available"
            >
              <span class="fallback-bolt" aria-hidden="true">ϟ</span>
              <span class="fallback-title">Image unavailable</span>
              <span class="fallback-description">
                No product photo has been provided.
              </span>
            </div>
          </div>

          <div class="visual-caption">
            <span class="caption-dot"></span>
            ElectroHub Component
          </div>
        </div>

        <div class="product-info">
          <p class="eyebrow">ELECTROHUB PRODUCT</p>

          <h1>{{ product.name || 'Unnamed Component' }}</h1>

          <p class="product-description">
            Explore this electronic component from our inventory.
            Check the available stock and select your quantity below.
          </p>

          <div class="details-list">
            <div class="detail-row">
              <span>Component ID</span>
              <strong>#{{ product.id }}</strong>
            </div>

            <div class="detail-row">
              <span>Available Stock</span>
              <strong>{{ availableStock }} units</strong>
            </div>

            <div class="detail-row">
              <span>Availability</span>
              <strong
                  class="stock-status"
                  :class="{
                  'in-stock': availableStock > 0,
                  'out-of-stock': availableStock <= 0,
                }"
              >
                <span class="stock-dot"></span>
                {{ availableStock > 0 ? 'In stock' : 'Out of stock' }}
              </strong>
            </div>

            <div class="price-section">
              <span>Price per item</span>
              <strong>{{ formatPrice(product.price) }}</strong>
            </div>
          </div>

          <div v-if="authChecking" class="auth-notice" role="status">
            Checking login status...
          </div>

          <template v-else-if="isAuthenticated">
            <label class="quantity-label" for="product-quantity">
              Quantity
            </label>

            <div class="quantity-control">
              <button
                  type="button"
                  aria-label="Decrease quantity"
                  :disabled="quantity <= 1 || availableStock <= 0"
                  @click="decreaseQuantity"
              >
                −
              </button>

              <input
                  id="product-quantity"
                  type="number"
                  inputmode="numeric"
                  min="1"
                  :max="availableStock"
                  :value="quantity"
                  :disabled="availableStock <= 0"
                  :aria-label="`Quantity for ${product.name}`"
                  @change="updateQuantity"
                  @keyup.enter="updateQuantity"
              />

              <button
                  type="button"
                  aria-label="Increase quantity"
                  :disabled="quantity >= availableStock || availableStock <= 0"
                  @click="increaseQuantity"
              >
                +
              </button>
            </div>

            <p class="stock-hint">
              Maximum available: {{ availableStock }} units
            </p>

            <div class="subtotal-row">
              <span>Subtotal</span>
              <strong>{{ formatPrice(subtotal) }}</strong>
            </div>

            <button
                type="button"
                class="primary-button add-to-cart-button"
                :disabled="!canAddToCart"
                @click="handleAddToCart"
            >
              <span v-if="addingToCart" class="button-spinner"></span>
              {{
                addingToCart
                    ? 'Adding to Cart...'
                    : availableStock <= 0
                        ? 'Out of Stock'
                        : 'Add to Cart'
              }}
            </button>

            <button
                type="button"
                class="secondary-button go-to-cart-button"
                @click="router.push('/cart')"
            >
              <span aria-hidden="true">🛒</span>
              Go to Cart
              <span v-if="cartItemCount > 0" class="cart-inline-count">
                ({{ cartItemCount }} {{ cartItemCount === 1 ? 'item' : 'items' }})
              </span>
              <span aria-hidden="true">→</span>
            </button>

            <p
                v-if="cartMessage"
                class="feedback-message success-message"
                role="status"
            >
              <span aria-hidden="true">✓</span>
              {{ cartMessage }}
            </p>

            <p
                v-if="cartError"
                class="feedback-message error-message"
                role="alert"
            >
              {{ cartError }}
            </p>

            <button
                type="button"
                class="secondary-button"
                @click="router.push('/components')"
            >
              Go to Inventory
              <span aria-hidden="true">→</span>
            </button>
          </template>

          <template v-else>
            <div class="login-notice">
              <strong>Sign in to continue</strong>
              <p>
                Log in to your ElectroHub account to add this
                component to your cart.
              </p>
            </div>

            <button
                type="button"
                class="primary-button"
                @click="goToLogin"
            >
              Login to Add to Cart
              <span aria-hidden="true">→</span>
            </button>
          </template>

          <p class="secure-note">
            <span aria-hidden="true">✓</span>
            Product availability is based on current inventory data.
          </p>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
.details-page {
  min-height: 100vh;
  padding: 36px 24px 64px;
  background: #f7f6fc;
  color: #211936;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.page-container {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
}

.top-navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 26px;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  margin: 0 0 34px;
  padding: 10px 0;
  border: 0;
  background: transparent;
  color: #6038c6;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

.back-button:hover {
  color: #3f2195;
}

.cart-navigation-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-height: 44px;
  padding: 10px 16px;
  border: 1px solid #ded5f2;
  border-radius: 12px;
  background: #fff;
  color: #6038c6;
  font: inherit;
  font-size: 14px;
  font-weight: 750;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(47, 28, 86, 0.05);
}

.cart-navigation-button:hover {
  border-color: #b9a4eb;
  background: #f8f5ff;
}

.cart-icon {
  font-size: 18px;
  line-height: 1;
}

.cart-count,
.cart-inline-count {
  font-size: 12px;
  font-weight: 800;
}

.cart-count {
  display: inline-grid;
  min-width: 22px;
  height: 22px;
  padding: 0 5px;
  place-items: center;
  border-radius: 999px;
  background: #7045d5;
  color: #fff;
}

.go-to-cart-button {
  margin-top: 12px;
}

.back-button:focus-visible,
button:focus-visible,
input:focus-visible {
  outline: 3px solid #bba6ff;
  outline-offset: 3px;
}

.product-card {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  align-items: center;
  gap: clamp(28px, 4vw, 56px);
  max-width: 1136px;
  margin: 0 auto;
  padding: clamp(24px, 4vw, 46px);
  background: #fff;
  border: 1px solid #ebe5f6;
  border-radius: 26px;
  box-shadow: 0 20px 60px rgba(47, 28, 86, 0.08);
}

.product-visual,
.product-info {
  min-width: 0;
}

.image-label {
  margin: 0 0 12px 2px;
  color: #706584;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.7px;
}

.product-image {
  display: grid;
  min-height: 360px;
  overflow: hidden;
  place-items: center;
  border: 1px solid #eee7ff;
  border-radius: 22px;
  background:
      radial-gradient(ellipse at 50% 40%, #fff 0%, transparent 65%),
      linear-gradient(145deg, #eee7ff 0%, #f8f5ff 100%);
}

.product-photo {
  display: block;
  width: 100%;
  height: 360px;
  padding: 22px;
  object-fit: contain;
}

.product-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  min-height: 300px;
  padding: 24px;
  text-align: center;
}

.fallback-bolt {
  color: #ed8658;
  font-size: 82px;
  line-height: 1;
}

.fallback-title {
  color: #403553;
  font-size: 16px;
  font-weight: 750;
}

.fallback-description {
  max-width: 230px;
  color: #716782;
  font-size: 13px;
  line-height: 1.5;
}

.visual-caption {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  color: #716782;
  font-size: 13px;
}

.caption-dot,
.stock-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 8px;
  border-radius: 50%;
  background: #21a366;
}

.eyebrow {
  margin: 0 0 18px;
  color: #7043d1;
  font-size: 12px;
  font-weight: 850;
  letter-spacing: 2px;
}

.product-info h1 {
  margin: 0 0 14px;
  color: #211936;
  font-size: clamp(30px, 3.5vw, 44px);
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -1px;
  overflow-wrap: anywhere;
}

.product-description {
  margin: 0 0 26px;
  color: #6f667f;
  font-size: 15px;
  line-height: 1.75;
}

.details-list {
  margin-bottom: 22px;
}

.detail-row,
.price-section,
.subtotal-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 17px 0;
  border-bottom: 1px solid #eeeaf4;
}

.detail-row > span,
.price-section > span,
.subtotal-row > span {
  color: #6e657d;
  font-size: 15px;
}

.detail-row strong {
  color: #211936;
  font-size: 15px;
  text-align: right;
  overflow-wrap: anywhere;
}

.stock-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.in-stock {
  color: #148044 !important;
}

.out-of-stock {
  color: #c13243 !important;
}

.out-of-stock .stock-dot {
  background: #c13243;
}

.price-section strong,
.subtotal-row strong {
  color: #633bd0;
  font-size: 22px;
  font-weight: 800;
  text-align: right;
}

.quantity-label {
  display: block;
  margin: 24px 0 11px;
  color: #211936;
  font-size: 15px;
  font-weight: 750;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quantity-control button {
  display: grid;
  width: 46px;
  height: 46px;
  flex: 0 0 46px;
  place-items: center;
  border: 1px solid #dfd4f7;
  border-radius: 11px;
  background: #f8f5ff;
  color: #6038c6;
  font-size: 23px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.quantity-control button:hover:not(:disabled) {
  border-color: #8b69e0;
  background: #eee7ff;
}

.quantity-control button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.quantity-control input {
  width: 92px;
  height: 46px;
  padding: 8px;
  border: 1px solid #dcd3ed;
  border-radius: 11px;
  background: #fff;
  color: #211936;
  font: inherit;
  font-weight: 700;
  text-align: center;
}

.stock-hint {
  margin: 9px 0 0;
  color: #7c728d;
  font-size: 12px;
}

.subtotal-row {
  margin-top: 12px;
  padding: 18px 0;
}

.subtotal-row > span {
  font-weight: 750;
}

.primary-button,
.secondary-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  min-height: 52px;
  margin-top: 20px;
  padding: 14px 18px;
  border: 1px solid transparent;
  border-radius: 11px;
  font: inherit;
  font-size: 15px;
  font-weight: 750;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, transform 0.2s;
}

.primary-button {
  background: #7045d5;
  color: #fff;
}

.primary-button:hover:not(:disabled) {
  background: #5932b8;
  transform: translateY(-1px);
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.secondary-button {
  margin-top: 12px;
  border-color: #ded5f2;
  background: #fff;
  color: #6038c6;
}

.secondary-button:hover {
  border-color: #b9a4eb;
  background: #f8f5ff;
}

.feedback-message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 14px 0 0;
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.success-message {
  border: 1px solid #bce7cb;
  background: #f0fbf4;
  color: #176c38;
}

.error-message {
  border: 1px solid #f0c6cc;
  background: #fff4f5;
  color: #a62a3b;
}

.login-notice {
  margin-top: 22px;
  padding: 16px;
  border: 1px solid #e8defa;
  border-radius: 12px;
  background: #faf7ff;
}

.login-notice strong {
  color: #302247;
  font-size: 14px;
}

.login-notice p {
  margin: 7px 0 0;
  color: #716782;
  font-size: 13px;
  line-height: 1.6;
}

.auth-notice {
  margin-top: 24px;
  padding: 14px;
  border-radius: 10px;
  background: #f5f1ff;
  color: #6038c6;
  font-size: 14px;
}

.secure-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 18px 0 0;
  color: #81778f;
  font-size: 12px;
  line-height: 1.6;
}

.secure-note span {
  color: #168044;
  font-weight: 800;
}

.message-card {
  max-width: 540px;
  margin: 60px auto;
  padding: 36px;
  border: 1px solid #ebe5f6;
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 15px 40px rgba(47, 28, 86, 0.06);
  text-align: center;
}

.message-card h2 {
  margin: 14px 0 8px;
  color: #211936;
}

.message-card p {
  color: #6f667f;
  line-height: 1.6;
}

.message-icon {
  color: #7045d5;
  font-size: 40px;
  font-weight: 800;
}

.loading-spinner,
.button-spinner {
  display: inline-block;
  border: 3px solid #e4daf9;
  border-top-color: #7045d5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-spinner {
  width: 34px;
  height: 34px;
}

.button-spinner {
  width: 17px;
  height: 17px;
  border-color: rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 760px) {
  .details-page {
    padding: 22px 16px 40px;
  }

  .top-navigation {
    margin-bottom: 22px;
  }

  .back-button {
    margin-bottom: 0;
    font-size: 14px;
  }

  .cart-navigation-button {
    gap: 6px;
    min-height: 40px;
    padding: 8px 10px;
    font-size: 13px;
  }

  .product-card {
    grid-template-columns: minmax(0, 1fr);
    gap: 28px;
    padding: 22px;
    border-radius: 20px;
  }

  .product-image {
    min-height: 240px;
  }

  .product-photo {
    height: 260px;
  }

  .product-icon {
    min-height: 240px;
  }

  .product-info h1 {
    font-size: clamp(29px, 8vw, 38px);
  }
}

@media (max-width: 380px) {
  .product-card {
    padding: 16px;
  }

  .detail-row,
  .price-section,
  .subtotal-row {
    gap: 10px;
  }

  .detail-row > span,
  .price-section > span,
  .subtotal-row > span {
    font-size: 13px;
  }

  .price-section strong,
  .subtotal-row strong {
    font-size: 19px;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
</style>

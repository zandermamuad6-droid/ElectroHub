
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getComponents } from '../services/api'

const route = useRoute()
const router = useRouter()

const product = ref(null)
const loading = ref(true)
const error = ref('')
const imageError = ref(false)

const productImage = computed(() => {
  return product.value?.image_url && !imageError.value
      ? product.value.image_url
      : null
})

function formatPrice(price) {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(Number(price) || 0)
}

function handleImageError() {
  imageError.value = true
}

onMounted(async () => {
  try {
    const data = await getComponents()
    const products = Array.isArray(data) ? data : data?.results || []
    const productId = Number(route.params.id)

    product.value = products.find(
        item => Number(item.id) === productId,
    ) || null

    if (!product.value) {
      error.value = 'Product not found.'
    }
  } catch (err) {
    error.value = err.message || 'Unable to load product details.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="details-page">
    <button class="back-button" @click="router.push('/')">
      ← Back to Home
    </button>

    <p v-if="loading" class="status-message">
      Loading product details...
    </p>

    <section v-else-if="error" class="message-card">
      <div class="message-icon">⌕</div>
      <h2>Product unavailable</h2>
      <p class="error-message">{{ error }}</p>

      <button class="primary-button" @click="router.push('/')">
        Browse Products
      </button>
    </section>

    <section v-else-if="product" class="product-card">
      <div class="product-image">
        <img
            v-if="productImage"
            :src="productImage"
            :alt="product.name"
            class="product-photo"
            @error="handleImageError"
        />

        <div v-else class="product-icon" aria-label="Product image unavailable">
          ⚡
          <span>No image available</span>
        </div>
      </div>

      <div class="product-info">
        <p class="eyebrow">ELECTROHUB PRODUCT</p>
        <h1>{{ product.name }}</h1>

        <p class="product-description">
          Explore this electronic component from our inventory.
        </p>

        <div class="detail-row">
          <span>Product ID</span>
          <strong>#{{ product.id }}</strong>
        </div>

        <div class="detail-row">
          <span>Available Quantity</span>
          <strong>{{ product.quantity }}</strong>
        </div>

        <div class="detail-row">
          <span>Availability</span>
          <strong
              :class="{
              'out-of-stock': Number(product.quantity) <= 0,
              'in-stock': Number(product.quantity) > 0,
            }"
          >
            {{
              Number(product.quantity) > 0
                  ? 'In stock'
                  : 'Out of stock'
            }}
          </strong>
        </div>

        <div class="price-section">
          <span>Price</span>
          <strong>{{ formatPrice(product.price) }}</strong>
        </div>

        <button
            class="primary-button"
            @click="router.push('/login')"
        >
          Login to Get Started →
        </button>
      </div>
    </section>
  </main>
</template>

<style scoped>
.details-page {
  min-height: 100vh;
  padding: 48px 7%;
  background: #f8f7fc;
  color: #241b3d;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.back-button {
  border: none;
  background: transparent;
  color: #6541c8;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 32px;
}

.back-button:hover {
  color: #40218d;
}

.product-card {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px;
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  gap: 48px;
  align-items: center;
  background: white;
  border: 1px solid #eee9f8;
  border-radius: 24px;
  box-shadow: 0 16px 45px rgba(54, 33, 95, 0.07);
}

.product-image {
  min-width: 0;
  min-height: 320px;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 20px;
  background: linear-gradient(135deg, #eee7ff, #f7f3ff);
}

.product-photo {
  display: block;
  width: 100%;
  height: 320px;
  padding: 18px;
  object-fit: contain;
}

.product-icon {
  min-height: 280px;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  color: #7045d5;
  font-size: 100px;
}

.product-icon span {
  color: #81778f;
  font-size: 13px;
  font-weight: 500;
}

.product-info {
  min-width: 0;
}

.eyebrow {
  color: #7650ce;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 2px;
}

.product-info h1 {
  margin: 12px 0;
  font-size: clamp(28px, 4vw, 40px);
  overflow-wrap: anywhere;
}

.product-description {
  color: #777185;
  line-height: 1.7;
  margin-bottom: 28px;
}

.detail-row,
.price-section {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 0;
  border-bottom: 1px solid #eeeaf4;
}

.detail-row span,
.price-section span {
  color: #777185;
}

.detail-row strong {
  text-align: right;
  overflow-wrap: anywhere;
}

.in-stock {
  color: #16803d;
}

.out-of-stock {
  color: #c0394b;
}

.price-section strong {
  color: #6541c8;
  font-size: 23px;
}

.primary-button {
  width: 100%;
  margin-top: 28px;
  padding: 15px;
  border: none;
  border-radius: 10px;
  background: #7045d5;
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.primary-button:hover {
  background: #5932b8;
}

.status-message {
  text-align: center;
  margin-top: 80px;
  color: #777185;
}

.message-card {
  max-width: 500px;
  margin: 60px auto;
  padding: 36px;
  text-align: center;
  background: white;
  border: 1px solid #eee9f8;
  border-radius: 20px;
}

.message-icon {
  color: #7045d5;
  font-size: 40px;
}

.message-card h2 {
  margin-bottom: 8px;
}

.error-message {
  color: #c0394b;
}

@media (max-width: 700px) {
  .details-page {
    padding: 28px 5%;
  }

  .product-card {
    grid-template-columns: minmax(0, 1fr);
    padding: 22px;
    gap: 28px;
  }

  .product-image {
    min-height: 230px;
  }

  .product-photo {
    height: 260px;
  }

  .product-icon {
    min-height: 220px;
  }

  .detail-row,
  .price-section {
    gap: 12px;
  }
}
</style>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { getComponents } from '../services/api'

const router = useRouter()
const products = ref([])
const search = ref('')
const loading = ref(true)
const error = ref('')

const categories = [
  { name: 'Resistors', icon: '〰', keyword: 'resistor', color: 'blue' },
  { name: 'Capacitors', icon: '▤', keyword: 'capacitor', color: 'cyan' },
  { name: 'Transistors', icon: '⌁', keyword: 'transistor', color: 'indigo' },
  { name: 'Integrated Circuits', icon: '▦', keyword: 'integrated circuit', color: 'violet' },
  { name: 'LEDs', icon: '✳', keyword: 'led', color: 'amber' },
  { name: 'Other Components', icon: '⚙', keyword: '', color: 'slate' },
]

const filteredProducts = computed(() => {
  const keyword = search.value.trim().toLowerCase()

  if (!keyword) return products.value

  return products.value.filter(product =>
      String(product.name ?? '').toLowerCase().includes(keyword),
  )
})

const formatPrice = price =>
    new Intl.NumberFormat('en-PH', {
      style: 'currency',
      currency: 'PHP',
    }).format(Number(price) || 0)

function openProduct(product) {
  router.push(`/products/${product.id}`)
}

function selectCategory(category) {
  search.value = category.keyword

  document.getElementById('products')?.scrollIntoView({
    behavior: 'smooth',
  })
}

function handleImageError(event) {
  event.target.style.display = 'none'
  event.target.nextElementSibling?.classList.remove('fallback-hidden')
}

onMounted(async () => {
  try {
    const data = await getComponents()
    products.value = Array.isArray(data) ? data : data?.results || []
  } catch (err) {
    error.value =
        'Unable to load products. Please log in if required or try again.'
    console.error('Failed to load products:', err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="storefront">
    <header class="navbar">
      <RouterLink to="/" class="brand" aria-label="ElectroHub home">
        <span class="brand-icon">E</span>
        <span class="brand-name">Electro<span>Hub</span></span>
      </RouterLink>

      <nav class="nav-links" aria-label="Main navigation">
        <RouterLink to="/" class="nav-link active">Home</RouterLink>
        <a href="#products" class="nav-link">Products</a>
        <a href="#categories" class="nav-link">Categories</a>
      </nav>

      <div class="nav-actions">
        <RouterLink to="/login" class="login-link">Log in</RouterLink>
        <RouterLink to="/login" class="button button-primary nav-cta">
          Get Started <span aria-hidden="true">↗</span>
        </RouterLink>
      </div>
    </header>

    <main>
      <section class="hero">
        <div class="hero-copy">
          <div class="eyebrow">
            <span class="eyebrow-dot"></span>
            YOUR ELECTRONICS PARTNER
          </div>

          <h1>
            Power your next
            <span>great idea.</span>
          </h1>

          <p class="hero-description">
            Find the electronic components you need for school projects,
            experiments, repairs, and the ideas you have yet to build.
          </p>

          <form
              class="search-form"
              role="search"
              @submit.prevent="
              document.getElementById('products')?.scrollIntoView({
                behavior: 'smooth',
              })
            "
          >
            <span class="search-icon" aria-hidden="true">⌕</span>
            <input
                v-model="search"
                type="search"
                placeholder="Search components..."
                aria-label="Search products"
            />
            <button type="submit" class="search-button">Search</button>
          </form>

          <div class="hero-actions">
            <a href="#products" class="button button-primary">
              Explore products <span aria-hidden="true">→</span>
            </a>
            <a href="#categories" class="text-link">
              Browse categories <span aria-hidden="true">↗</span>
            </a>
          </div>

          <div class="hero-note">
            <span class="note-check">✓</span>
            <span>Simple shopping. Reliable components. Big ideas.</span>
          </div>
        </div>

        <div class="hero-art" aria-label="Electronic chip illustration">
          <div class="art-orbit orbit-one"></div>
          <div class="art-orbit orbit-two"></div>
          <div class="art-grid"></div>

          <div class="art-card">
            <div class="art-card-top">
              <span class="art-label">ELECTROHUB / COMPONENTS</span>
              <span class="live-indicator"></span>
            </div>

            <div class="chip-stage">
              <div class="chip-wire wire-top"></div>
              <div class="chip-wire wire-bottom"></div>
              <div class="chip-wire wire-left"></div>
              <div class="chip-wire wire-right"></div>

              <div class="main-chip">
                <div class="chip-inner">
                  <span class="chip-logo">E</span>
                  <span class="chip-caption">TECH / 01</span>
                </div>
              </div>

              <span class="circuit-node node-one"></span>
              <span class="circuit-node node-two"></span>
              <span class="circuit-node node-three"></span>
              <span class="circuit-node node-four"></span>
            </div>

            <div class="art-card-bottom">
              <div>
                <span class="art-bottom-label">BUILT FOR CREATORS</span>
                <strong>Ideas start here.</strong>
              </div>
              <span class="art-arrow">↗</span>
            </div>
          </div>

          <div class="floating-card floating-top">
            <span class="floating-icon">✳</span>
            <div>
              <strong>Explore more</strong>
              <span>Components for every project</span>
            </div>
          </div>

          <div class="floating-card floating-bottom">
            <span class="stock-dot"></span>
            <div>
              <strong>Inventory at a glance</strong>
              <span>Check product availability</span>
            </div>
          </div>
        </div>
      </section>

      <section class="benefit-strip" aria-label="Store highlights">
        <div class="benefit">
          <span class="benefit-icon">⌕</span>
          <div>
            <strong>Easy discovery</strong>
            <span>Find components quickly</span>
          </div>
        </div>
        <div class="benefit">
          <span class="benefit-icon">₱</span>
          <div>
            <strong>Clear pricing</strong>
            <span>Prices shown in PHP</span>
          </div>
        </div>
        <div class="benefit">
          <span class="benefit-icon">▦</span>
          <div>
            <strong>Live inventory</strong>
            <span>See current stock status</span>
          </div>
        </div>
      </section>

      <section id="categories" class="section categories-section">
        <div class="section-heading">
          <div>
            <span class="section-kicker">FIND YOUR COMPONENT</span>
            <h2>Browse by category</h2>
            <p>Start with the type of component your project needs.</p>
          </div>
          <a href="#products" class="section-link">
            View products <span aria-hidden="true">→</span>
          </a>
        </div>

        <div class="category-grid">
          <button
              v-for="category in categories"
              :key="category.name"
              type="button"
              class="category-card"
              @click="selectCategory(category)"
          >
            <span class="category-icon" :class="`tone-${category.color}`">
              {{ category.icon }}
            </span>
            <span class="category-name">{{ category.name }}</span>
            <span class="category-arrow" aria-hidden="true">↗</span>
          </button>
        </div>
      </section>

      <section id="products" class="section products-section">
        <div class="section-heading product-heading">
          <div>
            <span class="section-kicker">FROM OUR INVENTORY</span>
            <h2>
              {{ search ? 'Search results' : 'Explore components' }}
            </h2>
            <p>
              {{ search
                ? `Products matching “${search}”.`
                : 'Discover components for your next project.' }}
            </p>
          </div>

          <span class="product-count">
            <span class="count-dot"></span>
            {{ filteredProducts.length }}
            {{ filteredProducts.length === 1 ? 'product' : 'products' }}
          </span>
        </div>

        <div v-if="loading" class="state-panel">
          <span class="loading-spinner"></span>
          <strong>Loading components</strong>
          <p>Getting the latest products from inventory...</p>
        </div>

        <div v-else-if="error" class="state-panel error-panel">
          <span class="state-icon">!</span>
          <strong>We couldn't load the products</strong>
          <p>{{ error }}</p>
          <button type="button" class="button button-outline" @click="router.go(0)">
            Try again
          </button>
        </div>

        <div
            v-else-if="filteredProducts.length"
            class="product-grid"
        >
          <article
              v-for="product in filteredProducts"
              :key="product.id"
              class="product-card"
              role="link"
              tabindex="0"
              :aria-label="`View details for ${product.name}`"
              @click="openProduct(product)"
              @keydown.enter="openProduct(product)"
              @keydown.space.prevent="openProduct(product)"
          >
            <div class="product-image">
              <img
                  v-if="product.image_url"
                  :src="product.image_url"
                  :alt="product.name"
                  class="product-photo"
                  loading="lazy"
                  @error="handleImageError"
              />

              <span
                  class="product-symbol"
                  :class="{ 'fallback-hidden': Boolean(product.image_url) }"
                  aria-hidden="true"
              >E</span>

              <span class="product-badge">COMPONENT</span>
              <span class="image-corner" aria-hidden="true">↗</span>
            </div>

            <div class="product-info">
              <span class="product-category">Electronic component</span>
              <h3>{{ product.name }}</h3>

              <div class="product-bottom">
                <span class="product-price">
                  {{ formatPrice(product.price) }}
                </span>

                <span
                    class="stock-label"
                    :class="{ 'out-of-stock': product.quantity <= 0 }"
                >
                  <span class="stock-dot"></span>
                  {{ product.quantity > 0 ? 'In stock' : 'Out of stock' }}
                </span>
              </div>

              <button
                  type="button"
                  class="product-button"
                  :disabled="product.quantity <= 0"
                  @click.stop="router.push('/login')"
              >
                {{ product.quantity > 0 ? 'Login to purchase' : 'Unavailable' }}
                <span aria-hidden="true">→</span>
              </button>
            </div>
          </article>
        </div>

        <div v-else class="empty-state">
          <span class="empty-icon">⌕</span>
          <h3>
            {{ search ? 'No matching products' : 'Your store is getting ready' }}
          </h3>
          <p>
            {{
              search
                  ? 'Try another component name or clear your search.'
                  : 'Products added by the administrator will appear here.'
            }}
          </p>
          <button
              v-if="search"
              type="button"
              class="button button-outline"
              @click="search = ''"
          >
            Clear search
          </button>
        </div>
      </section>

      <section class="bottom-banner">
        <div class="banner-mark">E</div>
        <div class="banner-copy">
          <span class="section-kicker">READY TO BUILD SOMETHING?</span>
          <h2>Your next idea starts with the right component.</h2>
          <p>Sign in to access your ElectroHub account.</p>
        </div>
        <RouterLink to="/login" class="button banner-button">
          Get started <span aria-hidden="true">→</span>
        </RouterLink>
      </section>
    </main>

    <footer class="footer">
      <RouterLink to="/" class="brand footer-brand">
        <span class="brand-icon">E</span>
        <span class="brand-name">Electro<span>Hub</span></span>
      </RouterLink>
      <p>Electronic components for every idea.</p>
      <span class="copyright">© {{ new Date().getFullYear() }} ElectroHub</span>
    </footer>
  </div>
</template>

<style scoped>
:global(*) { box-sizing: border-box; }
:global(html) { scroll-behavior: smooth; scroll-padding-top: 24px; background: #07152f; }
:global(body) { margin: 0; background: #07152f; }

.storefront {
  --blue: #2485ff;
  --blue-dark: #0961d8;
  --navy: #07152f;
  --navy-soft: #0b2045;
  --panel: #102b58;
  --muted: #a9bfdf;
  --line: #244775;
  min-height: 100vh;
  color: #f2f7ff;
  background: #081a38;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  overflow: hidden;
}

.navbar {
  min-height: 78px; padding: 15px 7.5%; display: flex; align-items: center;
  justify-content: space-between; gap: 28px; border-bottom: 1px solid #203e6b;
  background: #06132b;
}
.brand { display: inline-flex; align-items: center; gap: 10px; text-decoration: none; color: #f4f8ff; white-space: nowrap; }
.brand-icon { width: 39px; height: 39px; display: grid; place-items: center; border-radius: 11px; background: linear-gradient(145deg, #43a2ff, #0757d8); color: white; font-size: 22px; font-weight: 900; box-shadow: 0 5px 18px #147bff55; }
.brand-name { font-size: 21px; font-weight: 850; letter-spacing: -.8px; }
.brand-name > span { color: #50a6ff; }
.nav-links, .nav-actions { display: flex; align-items: center; gap: 28px; }
.nav-link, .login-link { color: #b8cbe7; text-decoration: none; font-size: 13px; font-weight: 650; transition: color .2s; }
.nav-link:hover, .nav-link.active, .login-link:hover { color: #5db0ff; }
.button { display: inline-flex; align-items: center; justify-content: center; gap: 12px; min-height: 45px; padding: 12px 19px; border: 1px solid transparent; border-radius: 10px; font: inherit; font-size: 13px; font-weight: 750; text-decoration: none; cursor: pointer; transition: background .2s, color .2s, transform .2s, box-shadow .2s; }
.button-primary { background: linear-gradient(120deg, #238aff, #075fe0); color: #fff; box-shadow: 0 7px 22px #0872ff3d; }
.button-primary:hover { background: #1670e8; transform: translateY(-2px); box-shadow: 0 10px 24px #0872ff55; }
.nav-cta { min-height: 41px; padding: 10px 15px; }

.hero { position: relative; display: grid; grid-template-columns: 1.02fr .98fr; align-items: center; gap: 45px; padding: 76px 8% 78px; background: radial-gradient(ellipse at 78% 18%, #174f9d 0, transparent 38%), radial-gradient(ellipse at 4% 100%, #0e3471 0, transparent 45%), linear-gradient(125deg, #07152f 0%, #0a2450 54%, #0a3472 100%); }
.hero::after { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .16; background-image: linear-gradient(#8bbfff18 1px, transparent 1px), linear-gradient(90deg, #8bbfff18 1px, transparent 1px); background-size: 34px 34px; mask-image: linear-gradient(90deg, black, transparent 85%); }
.hero-copy { position: relative; z-index: 2; max-width: 580px; }
.eyebrow, .section-kicker { color: #69b5ff; font-size: 10px; font-weight: 850; letter-spacing: 1.6px; }
.eyebrow { display: inline-flex; align-items: center; gap: 9px; }
.eyebrow-dot, .count-dot, .stock-dot { width: 7px; height: 7px; flex: 0 0 7px; border-radius: 50%; background: #36dfaa; }
.hero h1 { margin: 23px 0 19px; color: #f6f9ff; font-size: clamp(42px, 5vw, 68px); line-height: 1.06; letter-spacing: -3px; font-weight: 850; }
.hero h1 span { display: block; color: #57aaff; }
.hero-description { max-width: 480px; margin: 0; color: #c0d1eb; font-size: 15px; line-height: 1.9; }
.search-form { display: flex; align-items: center; gap: 9px; max-width: 490px; margin-top: 29px; padding: 6px; border: 1px solid #4676b5; border-radius: 12px; background: #0d2851; box-shadow: 0 9px 30px #00000020; }
.search-icon { padding-left: 10px; color: #a9c6ed; font-size: 25px; line-height: 1; }
.search-form input { flex: 1; min-width: 0; padding: 11px 2px; border: 0; outline: 0; background: transparent; color: #fff; font: inherit; font-size: 13px; }
.search-form input::placeholder { color: #9eb6d8; }
.search-form:focus-within { border-color: #6eb6ff; box-shadow: 0 0 0 3px #2485ff30; }
.search-button { padding: 12px 17px; border: 0; border-radius: 8px; background: #2589ff; color: white; font: inherit; font-size: 12px; font-weight: 750; cursor: pointer; }
.search-button:hover { background: #0870ee; }
.hero-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 23px; margin-top: 22px; }
.text-link, .section-link { color: #d1e2fb; text-decoration: none; font-size: 12px; font-weight: 750; }
.text-link:hover, .section-link:hover { color: #65b4ff; }
.hero-note { display: flex; align-items: center; gap: 9px; margin-top: 28px; color: #adc3e3; font-size: 11px; }
.note-check { display: grid; place-items: center; width: 19px; height: 19px; border-radius: 50%; background: #123e60; color: #5be0b1; font-size: 11px; font-weight: 900; }

.hero-art { position: relative; min-height: 390px; display: grid; place-items: center; isolation: isolate; }
.art-grid { position: absolute; inset: 15px 0; z-index: -1; opacity: .65; background-image: radial-gradient(#7ebaff 1px, transparent 1px); background-size: 19px 19px; mask-image: radial-gradient(ellipse, black 20%, transparent 73%); }
.art-orbit { position: absolute; border: 1px solid #427dc4; border-radius: 50%; transform: rotate(-25deg); }
.orbit-one { width: 370px; height: 235px; }
.orbit-two { width: 310px; height: 370px; transform: rotate(42deg); border-color: #285da1; }
.art-card { position: relative; z-index: 1; width: min(100%, 370px); min-height: 305px; padding: 22px 23px 18px; border: 1px solid #3a70b5; border-radius: 22px; background: linear-gradient(145deg, #12376e, #071b3b); box-shadow: 0 25px 70px #00000045, inset 0 1px #ffffff16; }
.art-card-top, .art-card-bottom { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.art-label { color: #9fc4f1; font-size: 9px; font-weight: 850; letter-spacing: 1.3px; }
.live-indicator { width: 8px; height: 8px; border-radius: 50%; background: #28dca4; box-shadow: 0 0 0 4px #28ba801c; }
.chip-stage { position: relative; height: 190px; display: grid; place-items: center; }
.main-chip { position: relative; z-index: 2; width: 125px; height: 125px; display: grid; place-items: center; border: 8px solid #478de9; border-radius: 20px; background: linear-gradient(145deg, #2b9bff, #0640aa); box-shadow: 0 17px 35px #003c9c70, inset 0 1px #ffffff62; transform: rotate(-7deg); }
.chip-inner { width: 78px; height: 78px; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 1px solid #ffffff5c; border-radius: 11px; color: white; }
.chip-logo { font-size: 40px; font-weight: 900; line-height: 1; }
.chip-caption { margin-top: 5px; color: #cde5ff; font-size: 7px; letter-spacing: 1.5px; }
.chip-wire { position: absolute; z-index: 0; border-color: #64b2ff; border-style: solid; }
.wire-top, .wire-bottom { left: 50%; width: 75px; height: 36px; transform: translateX(-50%); }
.wire-top { top: 13px; border-width: 2px 2px 0; }
.wire-bottom { bottom: 12px; border-width: 0 2px 2px; }
.wire-left, .wire-right { top: 50%; width: 65px; height: 45px; transform: translateY(-50%); }
.wire-left { left: 15px; border-width: 2px 0 2px 2px; }
.wire-right { right: 15px; border-width: 2px 2px 2px 0; }
.circuit-node { position: absolute; z-index: 3; width: 9px; height: 9px; border: 2px solid #fff; border-radius: 50%; background: #55a7ff; box-shadow: 0 0 0 2px #5596ec; }
.node-one { top: 25px; left: 89px; } .node-two { top: 25px; right: 89px; } .node-three { bottom: 23px; left: 89px; } .node-four { right: 89px; bottom: 23px; }
.art-card-bottom { padding-top: 15px; border-top: 1px solid #2a4f80; }
.art-bottom-label, .art-card-bottom strong { display: block; }
.art-bottom-label { color: #a2c3eb; font-size: 8px; letter-spacing: 1.2px; font-weight: 800; }
.art-card-bottom strong { margin-top: 5px; color: #f4f8ff; font-size: 14px; }
.art-arrow { color: #5eb2ff; font-size: 22px; }
.floating-card { position: absolute; z-index: 3; display: flex; align-items: center; gap: 10px; padding: 12px 14px; border: 1px solid #35629a; border-radius: 12px; background: #0c2851; box-shadow: 0 12px 32px #00000035; }
.floating-top { top: 42px; right: -2px; } .floating-bottom { bottom: 34px; left: -7px; }
.floating-icon { width: 34px; height: 34px; display: grid; place-items: center; border-radius: 9px; background: #123f79; color: #70bbff; font-size: 21px; }
.floating-card strong, .floating-card span:not(.floating-icon):not(.stock-dot) { display: block; }
.floating-card strong { color: #f2f7ff; font-size: 10px; }
.floating-card div > span { margin-top: 4px; color: #a8bfdf; font-size: 9px; }

.benefit-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 23px 8%; border-top: 1px solid #204775; border-bottom: 1px solid #204775; background: #0b2450; }
.benefit { display: flex; align-items: center; justify-content: center; gap: 12px; }
.benefit-icon { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 11px; background: #123c78; color: #65b3ff; font-size: 19px; font-weight: 800; }
.benefit strong, .benefit span:last-child { display: block; }
.benefit strong { color: #f1f6ff; font-size: 12px; }
.benefit div span { margin-top: 4px; color: #a9bfdf; font-size: 10px; }

.section { padding: 72px 8%; }
.categories-section { border-bottom: 1px solid #244775; background: linear-gradient(140deg, #0a1d3e, #0b2a59); }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 20px; margin-bottom: 27px; }
.section-heading h2 { margin: 9px 0 7px; color: #f4f8ff; font-size: clamp(25px, 3vw, 34px); font-weight: 820; letter-spacing: -1.2px; }
.section-heading p { margin: 0; color: #aec2e0; font-size: 13px; line-height: 1.7; }
.section-link { display: inline-flex; align-items: center; gap: 8px; padding-bottom: 5px; white-space: nowrap; }
.category-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 14px; }
.category-card { position: relative; min-width: 0; min-height: 140px; display: flex; flex-direction: column; align-items: flex-start; justify-content: center; gap: 15px; padding: 17px; border: 1px solid #2a4e7e; border-radius: 14px; background: linear-gradient(145deg, #123364, #0c244b); color: #eaf3ff; text-align: left; font: inherit; font-size: 11px; font-weight: 750; cursor: pointer; transition: border-color .2s, background .2s, transform .2s, box-shadow .2s; }
.category-card:hover, .category-card:focus-visible { border-color: #5daaff; background: linear-gradient(145deg, #174783, #10305f); box-shadow: 0 10px 25px #00000025; transform: translateY(-3px); outline: none; }
.category-icon { width: 44px; height: 44px; display: grid; place-items: center; border-radius: 12px; font-size: 24px; font-weight: 800; }
.tone-blue { background: #164b8e; color: #79bcff; } .tone-cyan { background: #10516d; color: #67e0f2; } .tone-indigo { background: #303f91; color: #b3bdff; } .tone-violet { background: #513d91; color: #d3baff; } .tone-amber { background: #68501e; color: #ffd36e; } .tone-slate { background: #29476c; color: #bfd5f1; }
.category-arrow { position: absolute; top: 17px; right: 15px; color: #a9c9ef; font-size: 15px; }

.products-section { background: linear-gradient(145deg, #07152f, #0b2550 65%, #0c2c5b); }
.product-heading { margin-bottom: 30px; }
.product-count { display: inline-flex; align-items: center; gap: 8px; padding: 9px 12px; border: 1px solid #2d4f7c; border-radius: 20px; background: #102b55; color: #c1d3ed; font-size: 11px; font-weight: 700; white-space: nowrap; }
.count-dot { width: 6px; height: 6px; flex-basis: 6px; background: #45a1ff; }
.product-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 19px; }
.product-card { min-width: 0; overflow: hidden; border: 1px solid #254775; border-radius: 15px; background: #0d2650; cursor: pointer; transition: border-color .2s, transform .2s, box-shadow .2s; }
.product-card:hover, .product-card:focus-visible { border-color: #559fff; box-shadow: 0 15px 35px #00000035; transform: translateY(-4px); outline: none; }
.product-image { position: relative; height: 175px; display: grid; place-items: center; overflow: hidden; background: radial-gradient(circle at 50% 45%, #1a4b86 0, transparent 60%), linear-gradient(145deg, #123565, #091d3c); }
.product-photo { display: block; width: 100%; height: 100%; padding: 13px; object-fit: contain; transition: transform .25s; }
.product-card:hover .product-photo { transform: scale(1.04); }
.product-symbol { color: #4b9bff; font-size: 68px; font-weight: 900; line-height: 1; }
.fallback-hidden { display: none; }
.product-badge { position: absolute; top: 12px; left: 12px; padding: 6px 8px; border: 1px solid #35649b; border-radius: 5px; background: #0b2850e8; color: #a8d1ff; font-size: 8px; font-weight: 850; letter-spacing: .5px; }
.image-corner { position: absolute; right: 12px; bottom: 12px; width: 27px; height: 27px; display: grid; place-items: center; border: 1px solid #4775a8; border-radius: 8px; background: #0b2850e8; color: #a7d1ff; font-size: 14px; opacity: 0; transform: translateY(3px); transition: opacity .2s, transform .2s; }
.product-card:hover .image-corner, .product-card:focus-visible .image-corner { opacity: 1; transform: translateY(0); }
.product-info { padding: 17px; }
.product-category { color: #8fb3de; font-size: 9px; font-weight: 700; letter-spacing: .3px; text-transform: uppercase; }
.product-info h3 { min-height: 39px; margin: 8px 0 15px; color: #f1f6ff; font-size: 14px; font-weight: 750; line-height: 1.45; overflow-wrap: anywhere; }
.product-bottom { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; }
.product-price { color: #69b4ff; font-size: 16px; font-weight: 850; letter-spacing: -.3px; }
.stock-label { display: inline-flex; align-items: center; gap: 6px; color: #58dfac; font-size: 9px; font-weight: 750; }
.stock-label .stock-dot { width: 6px; height: 6px; flex-basis: 6px; }
.stock-label.out-of-stock { color: #ff9696; } .stock-label.out-of-stock .stock-dot { background: #ff6b78; }
.product-button { width: 100%; min-height: 39px; display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 17px; padding: 10px 12px; border: 1px solid #2c70ba; border-radius: 8px; background: #123b70; color: #b8dcff; font: inherit; font-size: 10px; font-weight: 800; cursor: pointer; transition: background .2s, color .2s, border-color .2s; }
.product-button:hover:not(:disabled) { border-color: #3c9bff; background: #2184f5; color: #fff; }
.product-button:disabled { border-color: #30445f; background: #1a2d49; color: #8296b2; cursor: not-allowed; }
.state-panel, .empty-state { min-height: 245px; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 35px 20px; border: 1px dashed #315886; border-radius: 16px; background: #0c2448; text-align: center; }
.state-panel strong, .empty-state h3 { margin: 12px 0 0; color: #f1f6ff; font-size: 16px; }
.state-panel p, .empty-state p { max-width: 450px; margin: 9px 0 0; color: #adc2e0; font-size: 12px; line-height: 1.8; }
.loading-spinner { width: 31px; height: 31px; border: 3px solid #214c80; border-top-color: #48a1ff; border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-panel .state-icon, .empty-icon { width: 44px; height: 44px; display: grid; place-items: center; border-radius: 13px; background: #16427b; color: #6bb7ff; font-size: 26px; font-weight: 800; }
.error-panel .state-icon { background: #562e48; color: #ffadbb; }
.button-outline { margin-top: 16px; border-color: #35659c; background: #12305b; color: #c2dfff; }
.button-outline:hover { border-color: #65aaff; background: #17447c; }
.empty-state h3 { margin-top: 17px; }

.bottom-banner { display: flex; align-items: center; gap: 22px; margin: 0 8% 65px; padding: 34px; border: 1px solid #2861a0; border-radius: 20px; background: radial-gradient(circle at 100% 0, #164b8c 0, transparent 42%), linear-gradient(110deg, #0e2b57, #0b2043); box-shadow: 0 15px 40px #00000020; }
.banner-mark { width: 59px; height: 59px; flex: 0 0 59px; display: grid; place-items: center; border-radius: 16px; background: linear-gradient(145deg, #39a1ff, #075bd8); color: white; font-size: 31px; font-weight: 900; box-shadow: 0 10px 25px #1764e83b; }
.banner-copy { flex: 1; }
.banner-copy h2 { max-width: 570px; margin: 8px 0; color: #f3f8ff; font-size: clamp(21px, 2.6vw, 29px); line-height: 1.25; letter-spacing: -.8px; }
.banner-copy p { margin: 0; color: #b2c7e5; font-size: 12px; line-height: 1.7; }
.banner-button { flex-shrink: 0; background: #2588ff; color: #fff; }
.banner-button:hover { background: #0965df; transform: translateY(-2px); }
.footer { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 18px; padding: 26px 8%; border-top: 1px solid #203e68; background: #051126; }
.footer .brand-icon { width: 33px; height: 33px; border-radius: 9px; font-size: 19px; }
.footer .brand-name { font-size: 18px; }
.footer p, .copyright { color: #91aaca; font-size: 11px; }
.footer p { margin: 0; }

@media (max-width: 1050px) {
  .navbar { padding-right: 5%; padding-left: 5%; }
  .hero { gap: 20px; padding-right: 5%; padding-left: 5%; }
  .hero h1 { font-size: clamp(40px, 5vw, 56px); }
  .floating-top { right: -5px; }
  .category-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .product-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .section { padding-right: 5%; padding-left: 5%; }
  .bottom-banner { margin-right: 5%; margin-left: 5%; }
  .footer { padding-right: 5%; padding-left: 5%; }
}
@media (max-width: 760px) {
  .navbar { gap: 14px; flex-wrap: wrap; }
  .nav-links { order: 3; width: 100%; justify-content: center; gap: 25px; padding: 8px 0 2px; }
  .nav-actions { gap: 15px; }
  .hero { grid-template-columns: 1fr; padding-top: 55px; padding-bottom: 35px; }
  .hero-copy { max-width: 650px; }
  .hero-art { min-height: 365px; margin-top: 10px; }
  .benefit-strip { gap: 15px; padding-right: 5%; padding-left: 5%; }
  .benefit { justify-content: flex-start; }
  .benefit-icon { flex-shrink: 0; }
  .benefit div span { line-height: 1.5; }
  .product-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .product-image { height: 155px; }
  .bottom-banner { flex-wrap: wrap; padding: 25px; }
  .banner-copy { flex-basis: calc(100% - 85px); }
  .banner-button { margin-left: 81px; }
}
@media (max-width: 520px) {
  .navbar { padding: 13px 5%; }
  .brand-icon { width: 34px; height: 34px; }
  .brand-name { font-size: 19px; }
  .nav-actions { gap: 10px; }
  .login-link { font-size: 12px; }
  .nav-cta { min-height: 37px; padding: 9px 11px; font-size: 11px; }
  .nav-links { gap: 20px; }
  .nav-link { font-size: 12px; }
  .hero { padding: 44px 5% 30px; }
  .hero h1 { margin-top: 19px; font-size: clamp(39px, 10vw, 49px); letter-spacing: -2px; }
  .hero-description { font-size: 13px; }
  .search-form { gap: 5px; }
  .search-form input { font-size: 12px; }
  .search-button { padding: 11px 12px; font-size: 11px; }
  .hero-actions { gap: 14px; }
  .hero-actions .button { padding: 11px 13px; font-size: 11px; }
  .text-link { font-size: 10px; }
  .hero-note { align-items: flex-start; font-size: 10px; line-height: 1.6; }
  .hero-art { min-height: 325px; margin: 0 -5px; }
  .art-card { width: min(100% - 24px, 340px); min-height: 285px; padding: 18px; }
  .chip-stage { height: 175px; }
  .main-chip { width: 110px; height: 110px; }
  .chip-inner { width: 68px; height: 68px; }
  .chip-logo { font-size: 34px; }
  .floating-card { gap: 7px; padding: 9px; }
  .floating-top { top: 12px; right: 0; }
  .floating-bottom { bottom: 12px; left: 0; }
  .floating-card strong { font-size: 9px; }
  .floating-card div > span { font-size: 8px; }
  .floating-icon { width: 28px; height: 28px; }
  .benefit-strip { grid-template-columns: 1fr; gap: 17px; padding: 21px 7%; }
  .benefit { justify-content: flex-start; }
  .section { padding: 47px 5%; }
  .section-heading { align-items: flex-start; flex-direction: column; gap: 12px; margin-bottom: 22px; }
  .section-heading h2 { font-size: 27px; }
  .section-heading p { font-size: 12px; }
  .category-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
  .category-card { min-height: 120px; padding: 13px; font-size: 11px; }
  .category-icon { width: 39px; height: 39px; font-size: 21px; }
  .product-heading { align-items: flex-start; }
  .product-grid { gap: 11px; }
  .product-image { height: 120px; }
  .product-photo { padding: 8px; }
  .product-badge { top: 7px; left: 7px; padding: 5px 6px; font-size: 7px; }
  .product-info { padding: 11px; }
  .product-category { font-size: 8px; }
  .product-info h3 { min-height: 39px; margin: 7px 0 11px; font-size: 12px; }
  .product-bottom { align-items: flex-start; flex-direction: column; gap: 7px; }
  .product-price { font-size: 14px; }
  .product-button { min-height: 36px; margin-top: 13px; padding: 9px; font-size: 9px; }
  .stock-label { font-size: 9px; }
  .bottom-banner { gap: 14px; margin: 0 5% 40px; padding: 20px; }
  .banner-mark { width: 44px; height: 44px; flex-basis: 44px; border-radius: 12px; font-size: 24px; }
  .banner-copy { flex-basis: calc(100% - 60px); }
  .banner-copy h2 { font-size: 20px; }
  .banner-copy p { font-size: 11px; }
  .banner-button { margin-left: 58px; }
  .footer { flex-direction: column; align-items: flex-start; padding: 24px 5%; }
}
@media (prefers-reduced-motion: reduce) {
  :global(html) { scroll-behavior: auto; }
  *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; }
}
</style>

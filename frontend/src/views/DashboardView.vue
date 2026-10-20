<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { getComponents, getCurrentUser, logoutUser } from '../services/api'

const router = useRouter()
const user = ref(null)
const loading = ref(true)
const logoutLoading = ref(false)
const errorMessage = ref('')

const username = computed(
    () => user.value?.display_name || user.value?.username || 'User',
)

const role = computed(() => {
  if (user.value?.is_superuser) return 'Administrator'
  if (user.value?.role === 'STAFF') return 'Staff'
  return 'User'
})

const components = ref([])
const componentsLoading = ref(true)
const componentsError = ref('')

const stats = computed(() => {
  const rows = components.value
  const lowStockCount = rows.filter((component) => Number(component.quantity ?? 0) <= 10).length
  const inventoryValue = rows.reduce(
      (total, component) => total + Number(component.price ?? 0) * Number(component.quantity ?? 0),
      0,
  )

  return [
    {
      label: 'Total Components',
      value: rows.length.toLocaleString(),
      icon: '▦',
      tone: 'blue',
      note: 'Component records in database',
    },
    {
      label: 'Low Stock Items',
      value: lowStockCount.toLocaleString(),
      icon: '⚠',
      tone: 'orange',
      note: 'Quantity of 10 or less',
    },
    {
      label: 'Inventory Value',
      value: inventoryValue.toLocaleString('en-PH', {
        style: 'currency',
        currency: 'PHP',
        maximumFractionDigits: 2,
      }),
      icon: '₱',
      tone: 'green',
      note: 'Based on price × quantity',
    },
    {
      label: 'Suppliers',
      value: '—',
      icon: '♙',
      tone: 'cyan',
      note: 'Supplier data is not connected',
    },
  ]
})

const chartBars = [28, 42, 35, 55, 48, 68, 53, 78, 63, 88]
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']

const categories = [
  { name: 'Resistors', percent: 28, color: '#278fff' },
  { name: 'Capacitors', percent: 24, color: '#56b7ff' },
  { name: 'ICs', percent: 20, color: '#35ddbd' },
  { name: 'Diodes', percent: 12, color: '#8b9cff' },
  { name: 'Transistors', percent: 10, color: '#7cdbff' },
  { name: 'Others', percent: 6, color: '#52739c' },
]

const recentComponents = computed(() => components.value.slice(0, 5))

const today = new Intl.DateTimeFormat('en-US', {
  month: 'long',
  day: 'numeric',
  year: 'numeric',
}).format(new Date())

onMounted(async () => {
  try {
    user.value = await getCurrentUser()
    if (!user.value) {
      await router.replace({ name: 'login' })
      return
    }

    try {
      const response = await getComponents()
      const rows = Array.isArray(response) ? response : response?.results
      components.value = Array.isArray(rows) ? rows : []
      if (!Array.isArray(rows)) {
        componentsError.value = 'The component API returned an unexpected response.'
      }
    } catch {
      componentsError.value = 'Could not load components from the Django API.'
    }
  } catch {
    errorMessage.value = 'Could not verify your session.'
    await router.replace({ name: 'login' })
  } finally {
    loading.value = false
    componentsLoading.value = false
  }
})

async function handleLogout() {
  if (logoutLoading.value) return

  logoutLoading.value = true
  errorMessage.value = ''

  try {
    await logoutUser()
    await router.replace({ name: 'login' })
  } catch (error) {
    errorMessage.value = error.message || 'Logout failed. Please try again.'
  } finally {
    logoutLoading.value = false
  }
}
</script>

<template>
  <div class="dashboard-shell">
    <aside class="sidebar">
      <RouterLink to="/" class="brand" aria-label="ElectroHub home">
        <div class="brand-logo">E</div>
        <div class="brand-copy">
          <strong>ElectroHub</strong>
          <span>Electronic Inventory System</span>
        </div>
      </RouterLink>

      <div class="sidebar-label">WORKSPACE</div>
      <nav class="navigation">
        <a class="nav-item active" href="#dashboard"><span class="nav-icon">⌂</span><span>Dashboard</span></a>
        <RouterLink to="/components" class="nav-item" active-class="active"><span class="nav-icon">▦</span><span>Components</span></RouterLink>
        <a class="nav-item" href="#categories"><span class="nav-icon">◇</span><span>Categories</span></a>
        <a class="nav-item" href="#suppliers"><span class="nav-icon">♙</span><span>Suppliers</span></a>
        <a class="nav-item" href="#transactions"><span class="nav-icon">⇄</span><span>Transactions</span></a>
        <a class="nav-item" href="#reports"><span class="nav-icon">▤</span><span>Reports</span></a>
        <a class="nav-item" href="#users"><span class="nav-icon">♧</span><span>Users</span></a>
      </nav>

      <div class="sidebar-bottom">
        <div class="profile">
          <div class="avatar">{{ username.charAt(0).toUpperCase() }}</div>
          <div class="profile-copy">
            <strong>{{ username }}</strong>
            <span>{{ role }}</span>
          </div>
        </div>
        <button class="logout-button" type="button" :disabled="logoutLoading" @click="handleLogout">
          <span>⇥</span>
          {{ logoutLoading ? 'Signing out...' : 'Sign out' }}
        </button>
      </div>
    </aside>

    <main id="dashboard" class="main-content">
      <header class="topbar">
        <div class="breadcrumb"><span>Workspace</span><span class="breadcrumb-separator">/</span><strong>Dashboard</strong></div>
        <div class="topbar-right">
          <span class="today">{{ today }}</span>
          <div class="top-avatar">{{ username.charAt(0).toUpperCase() }}</div>
        </div>
      </header>

      <section v-if="loading" class="loading-state">
        <span class="loading-spinner"></span>
        Checking your Django session...
      </section>

      <template v-else>
        <p v-if="errorMessage" class="error-banner" role="alert">{{ errorMessage }}</p>

        <section class="welcome-banner">
          <div class="welcome-copy">
            <span class="welcome-eyebrow"><span class="online-dot"></span> YOUR INVENTORY AT A GLANCE</span>
            <h1>Welcome back, <span>{{ username }}!</span></h1>
            <p>Keep your electronic components organized and up to date. Review your inventory workspace from one place.</p>
            <div class="welcome-actions">
              <RouterLink to="/components" class="primary-action">Explore components <span>→</span></RouterLink>
              <span class="welcome-chip"><span class="online-dot"></span> Session authenticated</span>
            </div>
          </div>
          <div class="welcome-art" aria-hidden="true">
            <div class="art-orbit orbit-one"></div>
            <div class="art-orbit orbit-two"></div>
            <div class="chip chip-main"><span>E</span><small>TECH / 01</small><i></i><i></i><i></i><i></i></div>
            <div class="chip chip-small">R</div>
            <div class="art-spark spark-one">✦</div>
            <div class="art-spark spark-two">✧</div>
          </div>
        </section>

        <section class="section-heading">
          <div><h2>Inventory overview</h2><p>Live totals from your connected component records where available.</p></div>
          <span class="period-pill"><span class="period-dot"></span> Current overview</span>
        </section>

        <section class="stats-grid">
          <article v-for="stat in stats" :key="stat.label" class="stat-card">
            <div class="stat-top">
              <div class="stat-icon" :class="stat.tone">{{ stat.icon }}</div>
              <span class="stat-dot" :class="stat.tone"></span>
            </div>
            <p class="stat-label">{{ stat.label }}</p>
            <div class="stat-value">{{ stat.value }}</div>
            <p class="stat-note">{{ stat.note }}</p>
          </article>
        </section>

        <section class="analytics-grid">
          <article class="panel inventory-panel">
            <div class="panel-heading">
              <div><h3>Inventory activity</h3><p>Sample visual until transaction data is connected</p></div>
              <span class="panel-icon">↗</span>
            </div>
            <div class="chart">
              <div class="chart-y-labels"><span>100</span><span>75</span><span>50</span><span>25</span><span>0</span></div>
              <div class="chart-area">
                <div class="chart-grid-line line-1"></div><div class="chart-grid-line line-2"></div><div class="chart-grid-line line-3"></div><div class="chart-grid-line line-4"></div>
                <div class="bar-row">
                  <div v-for="(bar, index) in chartBars" :key="months[index]" class="bar-column">
                    <div class="bar" :style="{ height: `${bar}%` }" :title="`${months[index]} sample value`"></div>
                    <span>{{ months[index] }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="chart-footnote"><span class="legend-dot"></span> Illustrative sample chart — not live database data</div>
          </article>

          <article id="categories" class="panel categories-panel">
            <div class="panel-heading">
              <div><h3>Component categories</h3><p>Illustrative distribution</p></div>
              <span class="panel-icon">◉</span>
            </div>
            <div class="category-visual">
              <div class="donut">
                <div class="donut-center"><span>Demo</span><strong>Data</strong></div>
              </div>
            </div>
            <div class="category-list">
              <div v-for="category in categories" :key="category.name" class="category-row">
                <span class="category-color" :style="{ background: category.color }"></span>
                <span class="category-name">{{ category.name }}</span>
                <strong>{{ category.percent }}%</strong>
              </div>
            </div>
          </article>
        </section>

        <section id="components" class="panel recent-panel">
          <div class="panel-heading recent-heading">
            <div><h3>Recent components</h3><p>{{ componentsError || (componentsLoading ? 'Loading component records…' : 'Showing component records from the Django API') }}</p></div>
            <RouterLink to="/components" class="view-all-button">View all <span>↗</span></RouterLink>
          </div>
          <div v-if="recentComponents.length" class="table-scroll">
            <table>
              <thead><tr><th>Component</th><th>Quantity</th><th>Price</th><th>Status</th></tr></thead>
              <tbody>
              <tr v-for="component in recentComponents" :key="component.id">
                <td>{{ component.name }}</td><td>{{ component.quantity }}</td><td>{{ Number(component.price || 0).toLocaleString('en-PH', { style: 'currency', currency: 'PHP' }) }}</td><td><span class="status-pill" :class="{ 'low-stock-pill': Number(component.quantity || 0) <= 10 }">{{ Number(component.quantity || 0) <= 10 ? 'Low stock' : 'In stock' }}</span></td>
              </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">▦</div>
            <strong>{{ componentsLoading ? 'Loading components…' : componentsError ? 'Components could not be loaded' : 'No components found yet' }}</strong>
            <p>{{ componentsError || (componentsLoading ? 'Fetching records from Django.' : 'Add a component to your inventory to see it here.') }}</p>
            <RouterLink to="/components" class="empty-link">Open components <span>→</span></RouterLink>
          </div>
        </section>

        <footer class="page-footer">
          <span>© {{ new Date().getFullYear() }} ElectroHub · Electronic Inventory System</span>
          <span>Designed for organized inventory management</span>
        </footer>
      </template>
    </main>
  </div>
</template>

<style>
.dashboard-shell {
  --navy: #061329;
  --navy-2: #0a2042;
  --navy-3: #102f59;
  --blue: #278fff;
  --blue-light: #56adff;
  --mint: #35ddbd;
  --text: #f4f7ff;
  --muted: #9db5d6;
  --line: rgba(116, 166, 224, 0.18);
  min-height: 100vh;
  display: flex;
  background: var(--navy);
  color: var(--text);
  font-family: Inter, Arial, sans-serif;
}

.sidebar {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  flex: 0 0 250px;
  flex-direction: column;
  width: 250px;
  height: 100vh;
  padding: 25px 16px 18px;
  border-right: 1px solid var(--line);
  background: #07172f;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0 8px 30px;
  text-decoration: none;
}

.brand-logo {
  display: grid;
  flex-shrink: 0;
  place-items: center;
  width: 43px;
  height: 43px;
  border: 1px solid rgba(255,255,255,.15);
  border-radius: 13px;
  background: linear-gradient(140deg, #39a1ff, #075ce5);
  box-shadow: 0 7px 20px rgba(19,113,255,.25);
  color: white;
  font-size: 25px;
  font-weight: 850;
}

.brand-copy { display: grid; gap: 4px; min-width: 0; }
.brand-copy strong { color: #f5f8ff; font-size: 14px; font-weight: 800; }
.brand-copy span { color: #91acd2; font-size: 10px; }

.sidebar-label {
  padding: 0 12px 12px;
  color: #6282a9;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.3px;
}

.navigation { display: grid; gap: 6px; }

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 44px;
  padding: 0 12px;
  border: 1px solid transparent;
  border-radius: 11px;
  color: #9bb2d1;
  font-size: 13px;
  text-decoration: none;
  transition: background .2s, color .2s, border-color .2s;
}

.nav-item:hover,
.nav-item.active {
  border-color: rgba(71, 155, 255, .16);
  background: linear-gradient(100deg, rgba(39,143,255,.19), rgba(39,143,255,.06));
  color: #70baff;
}
.nav-item.active { font-weight: 750; }
.nav-icon { display: grid; place-items: center; width: 20px; font-size: 19px; }

.sidebar-bottom { margin-top: auto; padding-top: 18px; border-top: 1px solid var(--line); }
.profile { display: flex; align-items: center; gap: 10px; padding: 0 6px 18px; }
.avatar, .top-avatar {
  display: grid;
  flex-shrink: 0;
  place-items: center;
  width: 36px;
  height: 36px;
  border: 1px solid rgba(100, 177, 255, .25);
  border-radius: 50%;
  background: #123d70;
  color: #8ac9ff;
  font-weight: 800;
}
.profile-copy { display: grid; min-width: 0; gap: 4px; }
.profile-copy strong { overflow: hidden; color: #eaf3ff; font-size: 12px; text-overflow: ellipsis; }
.profile-copy span { color: #83a1c8; font-size: 11px; }

.logout-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  width: 100%;
  min-height: 40px;
  border: 1px solid #294c75;
  border-radius: 10px;
  background: #0b2140;
  color: #a8c6eb;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: .2s;
}
.logout-button:hover:not(:disabled) { border-color: #398eea; background: #102e54; color: white; }
.logout-button:disabled { cursor: wait; opacity: .6; }

.main-content {
  flex: 1;
  min-width: 0;
  max-width: 1800px;
  margin: 0 auto;
  padding: 0 32px 24px;
  background:
      radial-gradient(ellipse at 90% 40%, rgba(17, 71, 132, .15), transparent 40%),
      #091a34;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 76px;
  border-bottom: 1px solid var(--line);
}
.breadcrumb, .topbar-right { display: flex; align-items: center; gap: 12px; font-size: 12px; }
.breadcrumb { color: #819bbd; }
.breadcrumb strong { color: #e7f1ff; }
.breadcrumb-separator { color: #49698f; }
.topbar-right { color: #91acd2; }
.top-avatar { width: 34px; height: 34px; border-radius: 11px; background: linear-gradient(135deg,#278fff,#075ce5); color: white; }

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 260px;
  color: #a8bfdf;
  text-align: center;
}
.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid #315681;
  border-top-color: #45a4ff;
  border-radius: 50%;
  animation: dashboard-spin .7s linear infinite;
}
@keyframes dashboard-spin { to { transform: rotate(360deg); } }

.error-banner {
  padding: 12px 16px;
  border: 1px solid rgba(248,113,113,.28);
  border-radius: 10px;
  background: rgba(127,29,29,.22);
  color: #ffb4b4;
}

.welcome-banner {
  position: relative;
  display: flex;
  min-height: 235px;
  align-items: center;
  justify-content: space-between;
  overflow: hidden;
  margin-top: 26px;
  padding: 30px 36px;
  border: 1px solid rgba(95, 166, 255, .28);
  border-radius: 22px;
  background:
      radial-gradient(circle at 82% 40%, rgba(39,143,255,.22), transparent 32%),
      linear-gradient(112deg, #0d2a50 0%, #10396d 60%, #104580 100%);
  box-shadow: 0 18px 42px rgba(0,0,0,.16), inset 0 1px 0 rgba(255,255,255,.04);
  color: white;
}
.welcome-banner::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: .14;
  background-image: radial-gradient(#8ac9ff 1px, transparent 1px);
  background-size: 22px 22px;
  mask-image: linear-gradient(90deg, transparent 25%, black);
}
.welcome-copy { position: relative; z-index: 1; max-width: 610px; }
.welcome-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #70baff;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.7px;
}
.welcome-copy h1 { margin: 14px 0 10px; color: #f5f8ff; font-size: clamp(24px, 3vw, 34px); font-weight: 850; letter-spacing: -1px; }
.welcome-copy h1 span { color: #56adff; }
.welcome-copy p { max-width: 490px; margin: 0; color: #b1c8e7; font-size: 13px; line-height: 1.8; }
.welcome-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 14px; margin-top: 20px; }
.primary-action {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 11px 15px;
  border: 1px solid rgba(133,195,255,.28);
  border-radius: 9px;
  background: linear-gradient(110deg,#278fff,#075ee8);
  color: white;
  font-size: 11px;
  font-weight: 750;
  text-decoration: none;
  box-shadow: 0 8px 22px rgba(0,98,255,.2);
  transition: transform .2s, filter .2s;
}
.primary-action:hover { transform: translateY(-2px); filter: brightness(1.1); }
.primary-action span { font-size: 16px; }
.welcome-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 11px;
  border: 1px solid rgba(133,195,255,.2);
  border-radius: 30px;
  background: rgba(3,19,41,.25);
  color: #c4d8f2;
  font-size: 10px;
}
.online-dot { width: 7px; height: 7px; flex-shrink: 0; border-radius: 50%; background: #35ddbd; box-shadow: 0 0 10px rgba(53,221,189,.4); }

.welcome-art { position: relative; z-index: 1; flex: 0 0 220px; height: 175px; margin-right: 10px; }
.art-orbit { position: absolute; border: 1px solid rgba(110,185,255,.35); border-radius: 50%; }
.orbit-one { inset: 16px -8px; transform: rotate(-24deg); }
.orbit-two { inset: 31px 8px; transform: rotate(35deg); }
.chip {
  position: absolute;
  display: grid;
  place-items: center;
  border: 1px solid rgba(145,207,255,.7);
  border-radius: 13px;
  background: linear-gradient(145deg,#238df5,#0757c8);
  box-shadow: 0 15px 35px rgba(0,10,30,.3), inset 0 1px 0 rgba(255,255,255,.25);
  color: white;
  font-weight: 900;
}
.chip-main { top: 39px; left: 70px; width: 82px; height: 82px; font-size: 25px; transform: rotate(-12deg); }
.chip-main small { margin-top: -21px; color: #c6e4ff; font-size: 7px; font-weight: 700; letter-spacing: 1px; }
.chip-small { top: 88px; left: 20px; width: 45px; height: 45px; border-radius: 9px; font-size: 16px; transform: rotate(12deg); }
.chip i { position: absolute; width: 5px; height: 10px; border-radius: 3px; background: #83c7ff; }
.chip-main i:nth-of-type(1) { top: -7px; left: 17px; }
.chip-main i:nth-of-type(2) { top: -7px; right: 17px; }
.chip-main i:nth-of-type(3) { bottom: -7px; left: 17px; }
.chip-main i:nth-of-type(4) { right: 17px; bottom: -7px; }
.art-spark { position: absolute; color: #8bceff; }
.spark-one { top: 15px; right: 24px; font-size: 27px; }
.spark-two { right: 5px; bottom: 20px; font-size: 32px; }

.section-heading { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin: 30px 0 18px; }
.section-heading h2 { margin: 0; color: #f0f6ff; font-size: 18px; letter-spacing: -.3px; }
.section-heading p, .panel-heading p { margin: 7px 0 0; color: #8fa9cc; font-size: 11px; line-height: 1.6; }
.period-pill { display: inline-flex; align-items: center; gap: 8px; padding: 9px 12px; border: 1px solid #29496f; border-radius: 9px; background: #0b2241; color: #a8c6e9; font-size: 11px; }
.period-dot { width: 6px; height: 6px; border-radius: 50%; background: #35ddbd; }

.stats-grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 16px; }
.stat-card {
  min-width: 0;
  padding: 19px;
  border: 1px solid #203e64;
  border-radius: 16px;
  background: linear-gradient(145deg,#102a4c,#0b1e39);
  box-shadow: 0 7px 20px rgba(0,0,0,.1), inset 0 1px 0 rgba(255,255,255,.025);
  transition: transform .2s, border-color .2s;
}
.stat-card:hover { transform: translateY(-2px); border-color: #34679e; }
.stat-top { display: flex; align-items: center; justify-content: space-between; }
.stat-icon { display: grid; place-items: center; width: 39px; height: 39px; border-radius: 12px; font-size: 20px; font-weight: 800; }
.stat-icon.blue { background: rgba(39,143,255,.17); color: #63b5ff; }
.stat-icon.orange { background: rgba(245,158,11,.13); color: #ffc16b; }
.stat-icon.green { background: rgba(53,221,189,.13); color: #56e3c5; }
.stat-icon.cyan { background: rgba(86,183,255,.13); color: #7bcaff; }
.stat-dot { width: 7px; height: 7px; border-radius: 50%; }
.stat-dot.blue { background: #63b5ff; }
.stat-dot.orange { background: #ffc16b; }
.stat-dot.green { background: #56e3c5; }
.stat-dot.cyan { background: #7bcaff; }
.stat-label { margin: 17px 0 8px; color: #a4bad7; font-size: 11px; }
.stat-value { color: #f3f8ff; font-size: 26px; font-weight: 800; letter-spacing: -.8px; }
.stat-note { margin: 8px 0 0; color: #7795ba; font-size: 9px; line-height: 1.5; }

.analytics-grid { display: grid; grid-template-columns: minmax(0,1.65fr) minmax(260px,1fr); gap: 17px; margin-top: 18px; }
.panel {
  min-width: 0;
  padding: 22px;
  border: 1px solid #203e64;
  border-radius: 17px;
  background: linear-gradient(145deg,#102747,#0b1d37);
  box-shadow: 0 7px 20px rgba(0,0,0,.1);
}
.panel-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.panel-heading h3 { margin: 0; color: #edf5ff; font-size: 14px; }
.panel-icon { display: grid; place-items: center; width: 31px; height: 31px; border: 1px solid #2b527d; border-radius: 9px; background: rgba(39,143,255,.12); color: #70baff; font-size: 17px; }

.chart { display: flex; height: 205px; gap: 12px; margin-top: 27px; }
.chart-y-labels { display: flex; flex-direction: column; justify-content: space-between; padding-bottom: 22px; color: #7795ba; font-size: 9px; }
.chart-area { position: relative; flex: 1; min-width: 0; }
.chart-grid-line { position: absolute; right: 0; left: 0; height: 1px; border-top: 1px dashed rgba(112,157,207,.2); }
.line-1 { top: 0; }
.line-2 { top: 25%; }
.line-3 { top: 50%; }
.line-4 { top: 75%; }
.bar-row { position: absolute; inset: 0; display: flex; align-items: stretch; justify-content: space-around; gap: 7px; padding-top: 4px; }
.bar-column { z-index: 1; display: flex; flex: 1; flex-direction: column; align-items: center; justify-content: flex-end; gap: 9px; min-width: 0; }
.bar { width: min(100%,24px); min-height: 8px; border-radius: 5px 5px 2px 2px; background: linear-gradient(180deg,#65c2ff,#1475e7); opacity: .94; box-shadow: 0 0 13px rgba(39,143,255,.12); }
.bar-column span { color: #819dc0; font-size: 9px; }
.chart-footnote { display: flex; align-items: center; gap: 8px; margin-top: 16px; color: #819dc0; font-size: 10px; }
.legend-dot { width: 7px; height: 7px; border-radius: 50%; background: #278fff; }

.category-visual { display: grid; place-items: center; padding: 23px 0 18px; }
.donut { display: grid; place-items: center; width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(#278fff 0% 28%,#56b7ff 28% 52%,#35ddbd 52% 72%,#8b9cff 72% 84%,#7cdbff 84% 94%,#29476c 94% 100%); box-shadow: 0 0 28px rgba(39,143,255,.09); }
.donut-center { display: grid; place-content: center; width: 88px; height: 88px; border: 1px solid #24466e; border-radius: 50%; background: #0b203d; text-align: center; }
.donut-center span { color: #8fa9cc; font-size: 10px; }
.donut-center strong { margin-top: 3px; color: #f1f7ff; font-size: 15px; }
.category-list { display: grid; gap: 12px; }
.category-row { display: flex; align-items: center; gap: 9px; font-size: 10px; }
.category-color { width: 8px; height: 8px; border-radius: 3px; }
.category-name { flex: 1; color: #9bb4d4; }
.category-row strong { color: #e4efff; font-size: 10px; }

.recent-panel { margin-top: 18px; }
.recent-heading { margin-bottom: 18px; }
.view-all-button {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 11px;
  border: 1px solid #2a5684;
  border-radius: 8px;
  background: rgba(39,143,255,.12);
  color: #70baff;
  font-size: 11px;
  font-weight: 750;
  text-decoration: none;
  white-space: nowrap;
}
.view-all-button:hover { background: rgba(39,143,255,.2); }
.table-scroll { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; text-align: left; white-space: nowrap; }
thead { background: rgba(39,143,255,.07); }
th { padding: 13px 14px; color: #86a5ca; font-size: 10px; font-weight: 700; }
td { padding: 15px 14px; border-bottom: 1px solid rgba(116,166,224,.12); color: #d6e6fb; font-size: 11px; }
.status-pill { padding: 5px 9px; border: 1px solid rgba(53,221,189,.2); border-radius: 20px; background: rgba(53,221,189,.1); color: #75e8ce; font-size: 10px; }
.low-stock-pill { border-color: rgba(245,158,11,.25); background: rgba(245,158,11,.1); color: #ffc16b; }
.empty-state { display: grid; justify-items: center; padding: 27px 15px 19px; text-align: center; }
.empty-icon { display: grid; place-items: center; width: 45px; height: 45px; margin-bottom: 12px; border: 1px solid #2b527d; border-radius: 13px; background: rgba(39,143,255,.12); color: #70baff; font-size: 22px; }
.empty-state strong { color: #eaf3ff; font-size: 12px; }
.empty-state p { margin: 8px 0 0; color: #819dc0; font-size: 11px; line-height: 1.6; }
.empty-link { display: inline-flex; align-items: center; gap: 7px; margin-top: 15px; color: #70baff; font-size: 11px; font-weight: 750; text-decoration: none; }
.page-footer { display: flex; justify-content: space-between; gap: 16px; padding: 23px 3px 0; color: #7795ba; font-size: 10px; }

@media (max-width: 1150px) {
  .sidebar { flex-basis: 220px; width: 220px; }
  .main-content { padding-right: 22px; padding-left: 22px; }
  .stats-grid { grid-template-columns: repeat(2,minmax(0,1fr)); }
}
@media (max-width: 800px) {
  .sidebar { flex-basis: 190px; width: 190px; padding-right: 10px; padding-left: 10px; }
  .welcome-banner { padding: 27px 24px; }
  .welcome-art { flex-basis: 150px; margin-right: -20px; transform: scale(.8); }
  .analytics-grid { grid-template-columns: 1fr; }
}
@media (max-width: 580px) {
  .dashboard-shell { display: block; }
  .sidebar { position: static; width: 100%; height: auto; padding: 14px; border-right: 0; border-bottom: 1px solid var(--line); }
  .brand { padding-bottom: 15px; }
  .sidebar-label, .sidebar-bottom { display: none; }
  .navigation { display: flex; overflow-x: auto; gap: 5px; }
  .nav-item { flex: 0 0 auto; min-height: 38px; padding: 0 10px; font-size: 11px; }
  .nav-icon { font-size: 15px; }
  .main-content { padding: 0 14px 20px; }
  .topbar { min-height: 60px; }
  .today { display: none; }
  .welcome-banner { min-height: auto; margin-top: 18px; padding: 24px 20px; }
  .welcome-art { display: none; }
  .welcome-copy h1 { font-size: 26px; overflow-wrap: anywhere; }
  .section-heading { align-items: flex-start; }
  .period-pill { font-size: 9px; }
  .stats-grid { gap: 10px; }
  .stat-card { padding: 14px; }
  .stat-value { font-size: 23px; }
  .panel { padding: 16px; }
  .page-footer { flex-direction: column; gap: 7px; }
}
</style>

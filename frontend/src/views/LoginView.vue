
<template>
  <main class="login-page">
    <section class="login-card">
      <RouterLink to="/" class="brand" aria-label="ElectroHub home">
        <div class="brand-icon">E</div>

        <div class="brand-text">
          <h1>ElectroHub</h1>
          <p>Electronic Inventory System</p>
        </div>
      </RouterLink>

      <div class="welcome-section">
        <span class="eyebrow">
          <span class="status-dot"></span>
          YOUR INVENTORY, ONE PLACE
        </span>

        <h2>Welcome <span>back.</span></h2>
        <p>Sign in to access your inventory dashboard.</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Username</label>
          <input
              id="username"
              v-model="username"
              type="text"
              placeholder="Enter your username"
              autocomplete="username"
              required
              :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
              id="password"
              v-model="password"
              type="password"
              placeholder="Enter your password"
              autocomplete="current-password"
              required
              :disabled="loading"
          />
        </div>

        <p v-if="errorMessage" class="message error-message" role="alert">
          <span class="message-icon">!</span>
          {{ errorMessage }}
        </p>

        <p
            v-if="successMessage"
            class="message success-message"
            role="status"
        >
          <span class="message-icon">✓</span>
          {{ successMessage }}
        </p>

        <button type="submit" :disabled="loading" class="login-button">
          <span>{{ loading ? 'Signing in...' : 'Sign In' }}</span>
          <span v-if="!loading" class="button-arrow">→</span>
          <span v-else class="spinner" aria-hidden="true"></span>
        </button>
      </form>

      <div class="security-note">
        <span class="security-icon">▣</span>
        <span>Your account is protected by secure authentication.</span>
      </div>

      <p class="footer-text">
        © {{ currentYear }} ElectroHub
        <span class="footer-divider">·</span>
        Electronic Inventory System
      </p>
    </section>

    <div class="background-orbit orbit-one" aria-hidden="true"></div>
    <div class="background-orbit orbit-two" aria-hidden="true"></div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { loginUser } from '../services/api'

const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const currentYear = new Date().getFullYear()

function getSafeRedirect() {
  const redirect = route.query.redirect

  if (
      typeof redirect === 'string' &&
      redirect.startsWith('/') &&
      !redirect.startsWith('//') &&
      redirect !== '/login'
  ) {
    return redirect
  }

  return '/dashboard'
}

async function handleLogin() {
  if (loading.value) return

  errorMessage.value = ''
  successMessage.value = ''

  if (!username.value.trim() || !password.value) {
    errorMessage.value = 'Please enter your username and password.'
    return
  }

  loading.value = true

  try {
    const user = await loginUser(
        username.value.trim(),
        password.value,
    )

    successMessage.value =
        `Welcome, ${user.display_name || user.username}!`

    const redirect = getSafeRedirect()

    await router.replace(redirect)
  } catch (error) {
    console.error('Login or navigation error:', error)

    errorMessage.value =
        error.message || 'Unable to sign in. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  isolation: isolate;
  box-sizing: border-box;
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 36px 20px;
  background:
      radial-gradient(ellipse at 15% 20%, rgba(30, 115, 235, 0.2), transparent 42%),
      radial-gradient(ellipse at 85% 80%, rgba(15, 83, 184, 0.2), transparent 40%),
      linear-gradient(145deg, #061329 0%, #0a2042 52%, #10366b 100%);
  font-family: Inter, Arial, sans-serif;
  color: #f4f7ff;
}

.login-page::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  opacity: 0.18;
  background-image: radial-gradient(#69b5ff 1px, transparent 1px);
  background-size: 28px 28px;
  mask-image: linear-gradient(to bottom, black, transparent 85%);
}

.login-card {
  box-sizing: border-box;
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 460px;
  padding: 38px;
  border: 1px solid rgba(103, 166, 255, 0.32);
  border-radius: 22px;
  background: linear-gradient(145deg, rgba(17, 44, 83, 0.97), rgba(7, 24, 49, 0.98));
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(16px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 36px;
  text-decoration: none;
}

.brand-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 50px;
  height: 50px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 15px;
  background: linear-gradient(135deg, #39a1ff, #075ce5);
  color: white;
  font-size: 27px;
  font-weight: 850;
  box-shadow: 0 8px 24px rgba(19, 113, 255, 0.3);
}

.brand-text h1 {
  margin: 0;
  color: #f5f8ff;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.7px;
}

.brand-text p {
  margin: 5px 0 0;
  color: #91acd2;
  font-size: 12px;
}

.welcome-section {
  margin-bottom: 29px;
}

.eyebrow {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #68b4ff;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.3px;
}

.status-dot {
  width: 7px;
  height: 7px;
  flex-shrink: 0;
  border-radius: 50%;
  background: #35ddbd;
  box-shadow: 0 0 12px rgba(53, 221, 189, 0.5);
}

.welcome-section h2 {
  margin: 0 0 10px;
  color: #f5f8ff;
  font-size: 34px;
  font-weight: 850;
  line-height: 1.2;
  letter-spacing: -1.3px;
}

.welcome-section h2 span {
  color: #55a9ff;
}

.welcome-section > p {
  margin: 0;
  color: #a8bfdf;
  font-size: 14px;
  line-height: 1.7;
}

.form-group {
  margin-bottom: 21px;
}

.form-group label {
  display: block;
  margin-bottom: 9px;
  color: #dce9ff;
  font-size: 13px;
  font-weight: 650;
}

.form-group input {
  box-sizing: border-box;
  display: block;
  width: 100%;
  height: 50px;
  padding: 0 15px;
  border: 1px solid #315681;
  border-radius: 11px;
  outline: none;
  background: rgba(5, 20, 43, 0.72);
  color: #f5f8ff;
  font-family: inherit;
  font-size: 14px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.form-group input::placeholder {
  color: #718cad;
}

.form-group input:hover:not(:disabled) {
  border-color: #4c82bd;
}

.form-group input:focus {
  border-color: #3294ff;
  background: rgba(7, 27, 56, 0.95);
  box-shadow: 0 0 0 3px rgba(41, 137, 255, 0.17);
}

.form-group input:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.login-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  width: 100%;
  min-height: 51px;
  margin-top: 8px;
  padding: 0 18px;
  border: 1px solid rgba(126, 189, 255, 0.25);
  border-radius: 11px;
  background: linear-gradient(110deg, #278fff, #075ee8);
  color: #fff;
  font-family: inherit;
  font-size: 14px;
  font-weight: 750;
  cursor: pointer;
  box-shadow: 0 9px 24px rgba(0, 98, 255, 0.22);
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  filter: brightness(1.1);
  box-shadow: 0 13px 30px rgba(0, 98, 255, 0.32);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  box-shadow: none;
}

.button-arrow {
  font-size: 19px;
  line-height: 1;
}

.spinner {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  margin: 0 0 16px;
  padding: 12px 14px;
  border: 1px solid transparent;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.6;
  overflow-wrap: anywhere;
}

.message-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 19px;
  height: 19px;
  border: 1px solid currentColor;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 800;
}

.error-message {
  border-color: rgba(248, 113, 113, 0.25);
  background: rgba(127, 29, 29, 0.25);
  color: #ffb4b4;
}

.success-message {
  border-color: rgba(52, 211, 153, 0.25);
  background: rgba(6, 95, 70, 0.24);
  color: #8bf2c9;
}

.security-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 23px;
  color: #91acd2;
  font-size: 11px;
  line-height: 1.6;
  text-align: center;
}

.security-icon {
  color: #56adff;
  font-size: 14px;
}

.footer-text {
  margin: 25px 0 0;
  padding-top: 20px;
  border-top: 1px solid rgba(111, 155, 211, 0.17);
  color: #7895ba;
  font-size: 11px;
  text-align: center;
  letter-spacing: 0.2px;
}

.footer-divider {
  margin: 0 5px;
  color: #3e6c9f;
}

.background-orbit {
  position: absolute;
  z-index: -1;
  width: 350px;
  height: 350px;
  border: 1px solid rgba(80, 157, 255, 0.14);
  border-radius: 50%;
  pointer-events: none;
}

.orbit-one {
  top: -190px;
  right: -100px;
}

.orbit-two {
  bottom: -220px;
  left: -130px;
  width: 430px;
  height: 430px;
}

@media (max-width: 480px) {
  .login-page {
    padding: 20px 14px;
  }

  .login-card {
    padding: 28px 22px;
    border-radius: 18px;
  }

  .brand {
    margin-bottom: 30px;
  }

  .brand-text h1 {
    font-size: 20px;
  }

  .welcome-section h2 {
    font-size: 29px;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
</style>

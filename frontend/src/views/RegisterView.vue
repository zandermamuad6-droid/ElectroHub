<template>
  <main class="register-page">
    <section class="register-card">
      <div class="brand">ElectroHub</div>

      <h1>Create your account</h1>
      <p class="subtitle">
        Join ElectroHub and start shopping for electronics.
      </p>

      <form @submit.prevent="handleRegister">
        <label for="display_name">Full name</label>
        <input
            id="display_name"
            v-model.trim="form.display_name"
            type="text"
            placeholder="Enter your full name"
            required
        />

        <label for="username">Username</label>
        <input
            id="username"
            v-model.trim="form.username"
            type="text"
            placeholder="Choose a username"
            autocomplete="username"
            required
        />

        <label for="email">Email address</label>
        <input
            id="email"
            v-model.trim="form.email"
            type="email"
            placeholder="you@example.com"
            autocomplete="email"
            required
        />

        <label for="password">Password</label>
        <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="At least 8 characters"
            autocomplete="new-password"
            minlength="8"
            required
        />

        <label for="confirm_password">Confirm password</label>
        <input
            id="confirm_password"
            v-model="confirmPassword"
            type="password"
            placeholder="Enter your password again"
            autocomplete="new-password"
            required
        />

        <p v-if="errorMessage" class="error">
          {{ errorMessage }}
        </p>

        <p v-if="successMessage" class="success">
          {{ successMessage }}
        </p>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Create Account' }}
        </button>
      </form>

      <p class="login-link">
        Already have an account?
        <RouterLink to="/login">Log in</RouterLink>
      </p>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { registerUser } from '../services/api.js'

const router = useRouter()

const form = reactive({
  display_name: '',
  username: '',
  email: '',
  password: '',
})

const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''

  if (form.password !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  if (form.password.length < 8) {
    errorMessage.value = 'Password must contain at least 8 characters.'
    return
  }

  loading.value = true

  try {
    await registerUser({
      display_name: form.display_name,
      username: form.username,
      email: form.email,
      password: form.password,
    })

    successMessage.value =
        'Account created successfully! Redirecting to login...'

    setTimeout(() => {
      router.push('/login')
    }, 1200)
  } catch (error) {
    errorMessage.value =
        error.message || 'Unable to create your account.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 32px 16px;
  background: #f3f6fb;
}

.register-card {
  width: 100%;
  max-width: 460px;
  padding: 36px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  box-shadow: 0 12px 35px rgb(0 0 0 / 6%);
}

.brand {
  margin-bottom: 20px;
  color: #2563eb;
  font-size: 22px;
  font-weight: 800;
}

h1 {
  margin: 0 0 8px;
  color: #111827;
  font-size: 27px;
}

.subtitle {
  margin: 0 0 26px;
  color: #6b7280;
  line-height: 1.6;
}

form {
  display: flex;
  flex-direction: column;
}

label {
  margin: 14px 0 7px;
  color: #374151;
  font-size: 14px;
  font-weight: 600;
}

input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font: inherit;
  box-sizing: border-box;
}

input:focus {
  outline: 2px solid #93c5fd;
  border-color: #2563eb;
}

button {
  margin-top: 24px;
  padding: 13px;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

button:disabled {
  opacity: 0.65;
  cursor: wait;
}

.error {
  margin: 14px 0 0;
  color: #b91c1c;
  font-size: 14px;
}

.success {
  margin: 14px 0 0;
  color: #15803d;
  font-size: 14px;
}

.login-link {
  margin: 22px 0 0;
  color: #6b7280;
  font-size: 14px;
  text-align: center;
}

.login-link a {
  color: #2563eb;
  font-weight: 600;
  text-decoration: none;
}

@media (max-width: 480px) {
  .register-card {
    padding: 24px;
  }
}
</style>
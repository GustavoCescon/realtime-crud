<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''

  try {
    await auth.login({
      email: email.value.trim(),
      password: password.value,
    })

    await router.push({ name: 'home' })
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      errorMessage.value = 'E-mail ou senha inválidos.'
    } else {
      errorMessage.value = 'Não foi possível realizar o login. Tente novamente.'
    }
  }
}
</script>

<template>
  <main class="login-page">
    <form class="login-form" @submit.prevent="handleLogin">
      <h1>Entrar</h1>

      <label for="email">E-mail</label>
      <input
        id="email"
        v-model="email"
        type="email"
        autocomplete="username"
        required
      />

      <label for="password">Senha</label>
      <input
        id="password"
        v-model="password"
        type="password"
        autocomplete="current-password"
        required
      />

      <p v-if="errorMessage" role="alert" class="error">
        {{ errorMessage }}
      </p>

      <button type="submit" :disabled="auth.loading">
        {{ auth.loading ? 'Entrando...' : 'Entrar' }}
      </button>
    </form>
  </main>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
}

.login-form {
  width: min(100% - 2rem, 360px);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

input {
  padding: 10px;
}

button {
  padding: 12px;
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.error {
  color: #c62828;
}
</style>

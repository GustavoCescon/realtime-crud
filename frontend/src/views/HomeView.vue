<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

async function handleLogout() {
  try {
    await auth.logout()
  } catch (error) {
    console.error('Falha ao encerrar a sessão no servidor:', error)
  } finally {
    await router.push({ name: 'login' })
  }
}
</script>

<template>
  <main>
    <h1>Dashboard</h1>

    <p>Bem-vindo, {{ auth.user?.name }}!</p>
    <p>E-mail: {{ auth.user?.email }}</p>
    <p>Perfil: {{ auth.user?.role }}</p>

    <button :disabled="auth.loading" @click="handleLogout">
      {{ auth.loading ? 'Saindo...' : 'Sair' }}
    </button>
    <RouterLink v-if="auth.user?.role === 'admin'" to="/users">
        Gerenciar usuários
    </RouterLink>
  </main>
</template>

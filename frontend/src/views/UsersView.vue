<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { ApiError } from '@/services/api'
import { usersService } from '@/services/usersService'
import { useAuthStore } from '@/stores/auth'
import type { User } from '@/types/user'

const auth = useAuthStore()

const users = ref<User[]>([])
const loading = ref(false)
const errorMessage = ref('')

async function loadUsers() {
  if (!auth.accessToken) return

  loading.value = true
  errorMessage.value = ''

  try {
    users.value = await usersService.getAll(auth.accessToken)
  } catch (error) {
    if (error instanceof ApiError && error.status === 403) {
      errorMessage.value = 'Você não tem permissão para listar usuários.'
    } else {
      errorMessage.value = 'Não foi possível carregar os usuários.'
    }
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)
</script>

<template>
  <main>
    <h1>Usuários</h1>

    <p v-if="loading">Carregando usuários...</p>

    <p v-else-if="errorMessage" role="alert">
      {{ errorMessage }}
    </p>

    <p v-else-if="users.length === 0">
      Nenhum usuário encontrado.
    </p>

    <table v-else>
      <thead>
        <tr>
          <th>Nome</th>
          <th>E-mail</th>
          <th>Perfil</th>
          <th>Status</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.name }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.role }}</td>
          <td>{{ user.is_active ? 'Ativo' : 'Inativo' }}</td>
        </tr>
      </tbody>
    </table>
  </main>
</template>

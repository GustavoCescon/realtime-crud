import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authService } from '@/services/authService'
import {
  invalidateSession,
  registerTokenHandler,
} from '@/services/session'

import type { AuthUser, LoginRequest } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(null)
  const user = ref<AuthUser | null>(null)
  const loading = ref(false)
  const initialized = ref(false)
  let initializationPromise: Promise<void> | null = null

  const isAuthenticated = computed(
    () => accessToken.value !== null && user.value !== null,
  )

  async function login(credentials: LoginRequest) {
    loading.value = true

    try {
      invalidateSession()
      const response = await authService.login(credentials)

      accessToken.value = response.access_token
      user.value = await authService.me(response.access_token)
    } catch (error) {
      accessToken.value = null
      user.value = null
      throw error
    } finally {
      loading.value = false
    }
  }

  async function restoreSession() {
    loading.value = true

    try {
      const response = await authService.refresh()

      accessToken.value = response.access_token
      user.value = await authService.me(response.access_token)
    } catch {
      accessToken.value = null
      user.value = null
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    invalidateSession()
    user.value = null
    try {
      await authService.logout()
    } finally {
      loading.value = false
    }
  }
  async function initialize(): Promise<void> {
        if (initialized.value) return

        if (!initializationPromise) {
            initializationPromise = (async () => {
            try {
                await restoreSession()
            } finally {
                initialized.value = true
            }
            })()
        }

        await initializationPromise
    }
    registerTokenHandler({
      getToken: () => accessToken.value,
      setToken: (token) => {
        accessToken.value = token

        if (token === null) {
          user.value = null
        }
      },
    })
  return {
    accessToken,
    user,
    loading,
    initialized,
    isAuthenticated,
    login,
    restoreSession,
    initialize,
    logout,
  }
})

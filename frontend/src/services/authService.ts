import { apiRequest } from './api'
import type { AuthUser, LoginRequest, TokenResponse } from '@/types/auth'

export const authService = {
  login(data: LoginRequest): Promise<TokenResponse> {
    return apiRequest<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  me(accessToken: string): Promise<AuthUser> {
    return apiRequest<AuthUser>('/auth/me', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })
  },

  refresh(): Promise<TokenResponse> {
    return apiRequest<TokenResponse>('/auth/refresh', {
      method: 'POST',
    })
  },

  logout(): Promise<{ message: string }> {
    return apiRequest<{ message: string }>('/auth/logout', {
      method: 'POST',
    })
  },
}

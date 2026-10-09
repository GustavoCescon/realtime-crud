import { apiRequest } from './api'
import type { User } from '@/types/user'

export const usersService = {
  getAll(accessToken: string): Promise<User[]> {
    return apiRequest<User[]>(
      '/users',
      { method: 'GET' },
      accessToken,
    )
  },
}

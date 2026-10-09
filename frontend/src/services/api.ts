import {
  getAccessToken,
  refreshAccessToken,
} from './session'

const API_BASE_URL = '/api/v1'

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  async function send(accessToken?: string): Promise<Response> {
    const headers = new Headers(options.headers)

    if (options.body != null && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json')
    }

    if (accessToken) {
      headers.set('Authorization', `Bearer ${accessToken}`)
    }

    return fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include',
    })
  }

  let response = await send(token ?? getAccessToken() ?? undefined)

  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null)

    const code =
      body !== null &&
      typeof body === 'object' &&
      'code' in body &&
      typeof body.code === 'string'
        ? body.code
        : undefined

    if (
      response.status === 401 &&
      code === 'TOKEN_EXPIRED' &&
      endpoint !== '/auth/refresh' &&
      endpoint !== '/auth/login' &&
      token !== undefined
    ) {


      const newToken = await refreshAccessToken()
      response = await send(newToken)

    } else {
      throw new ApiError(
        response.status,
        `HTTP ${response.status}`,
        code,
      )
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, `HTTP ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

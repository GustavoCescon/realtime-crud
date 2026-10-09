import { authService } from './authService'

type TokenHandler = {
  getToken: () => string | null
  setToken: (token: string | null) => void
}

let tokenHandler: TokenHandler | null = null
let sessionVersion = 0
let refreshPromise: Promise<string> | null = null

export class SessionChangedError extends Error {
  constructor() {
    super('Session changed during refresh')
    this.name = 'SessionChangedError'
  }
}

export function registerTokenHandler(handler: TokenHandler): void {
  tokenHandler = handler
}

export function getAccessToken(): string | null {
  return tokenHandler?.getToken() ?? null
}

export function setAccessToken(token: string | null): void {
  tokenHandler?.setToken(token)
}

export function invalidateSession(): void {
  sessionVersion++
  setAccessToken(null)
  refreshPromise = null
}

export function refreshAccessToken(): Promise<string> {
  if (!refreshPromise) {
    const currentVersion = sessionVersion

    const pending = authService
      .refresh()
      .then((response) => {
        if (currentVersion !== sessionVersion) {
          throw new SessionChangedError()
        }

        setAccessToken(response.access_token)
        return response.access_token
      })
      .catch((error: unknown) => {
        if (currentVersion === sessionVersion) {
          invalidateSession()
        }

        throw error
      })

    const tracked = pending.finally(() => {
      if (refreshPromise === tracked) {
        refreshPromise = null
      }
    })

    refreshPromise = tracked
  }

  return refreshPromise
}

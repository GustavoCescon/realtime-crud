export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
}

export interface AuthUser {
  id: string
  name: string
  email: string
  role: string
  is_active: boolean
}

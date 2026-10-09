import { beforeEach, describe, expect, it, vi } from 'vitest'
import { apiRequest } from './api'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

describe('apiRequest', () => {
  beforeEach(() => {
        vi.restoreAllMocks()
        setActivePinia(createPinia())
    })

  it('deve retornar os dados quando a API responder 200', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch')

    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({
          id: '123',
          name: 'Gustavo',
        }),
        {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        },
      ),
    )

    const response = await apiRequest<{
      id: string
      name: string
    }>('/users/123')

    expect(response).toEqual({
      id: '123',
      name: 'Gustavo',
    })

    expect(fetchMock).toHaveBeenCalledOnce()
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/users/123',
      expect.objectContaining({
        credentials: 'include',
      }),
    )
  })

  it('deve renovar o token expirado e repetir a requisição', async () => {
  const auth = useAuthStore()

  auth.accessToken = 'token-antigo'

  const fetchMock = vi.spyOn(globalThis, 'fetch')

  fetchMock
    // 1. Requisição original: token expirado
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          code: 'TOKEN_EXPIRED',
          message: 'Token has expired',
        }),
        {
          status: 401,
          headers: { 'Content-Type': 'application/json' },
        },
      ),
    )

    // 2. Refresh: novo access token
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          access_token: 'token-novo',
        }),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        },
      ),
    )

    // 3. Repetição da requisição original
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify([
          {
            id: '123',
            name: 'Gustavo',
          },
        ]),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        },
      ),
    )

    const users = await apiRequest('/users', {}, auth.accessToken)

    expect(users).toEqual([
        {
        id: '123',
        name: 'Gustavo',
        },
    ])

    expect(fetchMock).toHaveBeenCalledTimes(3)

    expect(fetchMock).toHaveBeenNthCalledWith(
        2,
        '/api/v1/auth/refresh',
        expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        }),
    )

    expect(fetchMock).toHaveBeenNthCalledWith(
        3,
        '/api/v1/users',
        expect.objectContaining({
        headers: expect.any(Headers),
        }),
    )

    const retryOptions = fetchMock.mock.calls[2]?.[1]
    const retryHeaders = new Headers(retryOptions?.headers)

    expect(retryHeaders.get('Authorization')).toBe('Bearer token-novo')

    expect(auth.accessToken).toBe('token-novo')
  })
  it('deve limpar a sessão quando o refresh falhar', async () => {
        const auth = useAuthStore()

        auth.accessToken = 'token-expirado'
        auth.user = {
            id: '123',
            name: 'Gustavo',
            email: 'gustavo@example.com',
            role: 'admin',
            is_active: true,
        }

        const fetchMock = vi.spyOn(globalThis, 'fetch')

        fetchMock
            // Requisição original: access token expirado
            .mockResolvedValueOnce(
            new Response(
                JSON.stringify({
                code: 'TOKEN_EXPIRED',
                }),
                { status: 401 },
            ),
            )

            // Tentativa de refresh: cookie expirado
            .mockResolvedValueOnce(
            new Response(
                JSON.stringify({
                code: 'TOKEN_EXPIRED',
                }),
                { status: 401 },
            ),
            )

            await expect(
                apiRequest('/users', {}, auth.accessToken),
            ).rejects.toThrow('HTTP 401')

        expect(fetchMock).toHaveBeenCalledTimes(2)

        expect(auth.accessToken).toBeNull()
        expect(auth.user).toBeNull()
    })

    it('não deve restaurar o token após logout durante o refresh', async () => {
        const auth = useAuthStore()

        auth.accessToken = 'token-antigo'
        auth.user = {
            id: '123',
            name: 'Gustavo',
            email: 'gustavo@example.com',
            role: 'admin',
            is_active: true,
        }

        let resolveRefresh!: (response: Response) => void

        const pendingRefresh = new Promise<Response>((resolve) => {
            resolveRefresh = resolve
        })

        const fetchMock = vi.spyOn(globalThis, 'fetch')

        fetchMock
            // GET /users: access token expirado
            .mockResolvedValueOnce(
            new Response(
                JSON.stringify({ code: 'TOKEN_EXPIRED' }),
                { status: 401 },
            ),
            )
            // POST /auth/refresh: resposta ficará pendente
            .mockImplementationOnce(() => pendingRefresh)
            // POST /auth/logout: sucesso
            .mockResolvedValueOnce(
            new Response(
                JSON.stringify({ message: 'logged_out' }),
                { status: 200 },
            ),
            )

        // Inicia a requisição protegida.
        const requestPromise = apiRequest('/users', {}, auth.accessToken)

        // Aguarda até o refresh ter sido iniciado.
        await vi.waitFor(() => {
            expect(fetchMock).toHaveBeenCalledTimes(2)
        })

        // O usuário faz logout enquanto o refresh está pendente.
        await auth.logout()

        expect(auth.accessToken).toBeNull()
        expect(auth.user).toBeNull()

        // Agora o servidor finalmente responde ao refresh antigo.
        resolveRefresh(
            new Response(
            JSON.stringify({ access_token: 'token-novo' }),
            { status: 200 },
            ),
        )

        // A requisição original deve ser rejeitada.
        await expect(requestPromise).rejects.toThrow(
            'Session changed during refresh',
        )

        // O token antigo não pode ser restaurado.
        expect(auth.accessToken).toBeNull()
        expect(auth.user).toBeNull()

        // Não deve repetir GET /users após o logout.
        expect(fetchMock).toHaveBeenCalledTimes(3)
    })
})

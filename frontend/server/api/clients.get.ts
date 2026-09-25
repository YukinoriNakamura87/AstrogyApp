import { ofetch } from 'ofetch'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  try {
    return await ofetch(`${useRuntimeConfig().apiBase}/clients`, {
      query: {
        search: typeof query.search === 'string' && query.search ? query.search : undefined,
        sign: typeof query.sign === 'string' && query.sign ? query.sign : undefined,
      },
    })
  } catch (error: any) {
    throw createError({ statusCode: error.response?.status || 502, statusMessage: 'Client list loading failed', data: error.data })
  }
})

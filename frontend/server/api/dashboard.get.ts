import { ofetch } from 'ofetch'

export default defineEventHandler(async () => {
  try {
    return await ofetch(`${useRuntimeConfig().apiBase}/dashboard`)
  } catch (error: any) {
    throw createError({ statusCode: error.response?.status || 502, statusMessage: 'Dashboard loading failed', data: error.data })
  }
})

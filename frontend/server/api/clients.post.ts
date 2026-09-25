import { ofetch } from 'ofetch'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const apiBase = useRuntimeConfig().apiBase

  try {
    const client = await ofetch(`${apiBase}/clients`, { method: 'POST', body })
    setResponseStatus(event, 201)
    return client
  } catch (error: any) {
    throw createError({
      statusCode: error.response?.status || 502,
      statusMessage: 'Client registration failed',
      data: error.data,
    })
  }
})

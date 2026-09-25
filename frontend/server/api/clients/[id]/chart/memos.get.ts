import { ofetch } from 'ofetch'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id || !/^\d+$/.test(id)) {
    throw createError({ statusCode: 400, statusMessage: 'Invalid client ID' })
  }

  try {
    return await ofetch(`${useRuntimeConfig().apiBase}/clients/${id}/chart/memos`)
  } catch (error: any) {
    throw createError({
      statusCode: error.response?.status || 502,
      statusMessage: 'Chart memos loading failed',
      data: error.data,
    })
  }
})

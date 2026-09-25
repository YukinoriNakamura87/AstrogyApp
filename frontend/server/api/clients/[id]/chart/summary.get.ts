import { ofetch } from 'ofetch'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id || !/^\d+$/.test(id)) {
    throw createError({ statusCode: 400, statusMessage: 'Invalid client ID' })
  }

  try {
    const markdown = await ofetch<string>(`${useRuntimeConfig().apiBase}/clients/${id}/chart/summary`)
    setResponseHeader(event, 'content-type', 'text/markdown; charset=utf-8')
    return markdown
  } catch (error: any) {
    throw createError({
      statusCode: error.response?.status || 502,
      statusMessage: 'Chart summary export failed',
      data: error.data,
    })
  }
})

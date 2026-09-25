export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id || !/^\d+$/.test(id)) {
    throw createError({ statusCode: 400, statusMessage: 'Invalid client ID' })
  }

  try {
    return await $fetch(`${useRuntimeConfig().apiBase}/clients/${id}/chart/lilly-score`)
  } catch (error: any) {
    throw createError({
      statusCode: error.response?.status || 502,
      statusMessage: 'Lilly score calculation failed',
      data: error.data,
    })
  }
})

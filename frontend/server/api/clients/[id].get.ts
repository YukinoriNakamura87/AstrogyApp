export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  if (!id || !/^\d+$/.test(id)) {
    throw createError({ statusCode: 400, statusMessage: 'Invalid client ID' })
  }

  try {
    return await $fetch(`${useRuntimeConfig().apiBase}/clients/${id}`)
  } catch (error: any) {
    throw createError({
      statusCode: error.response?.status || 502,
      statusMessage: error.response?.status === 404 ? 'Client not found' : 'Client loading failed',
      data: error.data,
    })
  }
})

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const place = typeof query.q === 'string' ? query.q.trim() : ''

  if (place.length < 2) {
    throw createError({ statusCode: 400, statusMessage: '出生地は2文字以上で入力してください' })
  }

  try {
    return await $fetch(`${useRuntimeConfig().apiBase}/locations/search`, {
      query: { q: place },
    })
  } catch (error: any) {
    throw createError({
      statusCode: error.response?.status || 502,
      statusMessage: 'Birth place search failed',
      data: error.data,
    })
  }
})

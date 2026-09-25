export default defineNuxtConfig({
  devtools: { enabled: true },

  css: ['~/assets/css/main.css'],

  devServer: {
    host: '0.0.0.0',
    port: 3000,
  },

  runtimeConfig: {
    // Nuxt server routes call the backend over the Compose network.
    apiBase: process.env.NUXT_API_BASE || 'http://backend:8000',
  },
})

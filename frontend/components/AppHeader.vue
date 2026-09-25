<script setup lang="ts">
const route = useRoute()
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <NuxtLink to="/" class="brand" aria-label="Astrolabe ホーム">
        <span class="brand-mark"><span>✦</span></span>
        <span><strong>Astrolabe</strong><small>READING WORKSPACE</small></span>
      </NuxtLink>
      <nav class="main-nav" aria-label="メインナビゲーション">
        <NuxtLink to="/" :class="{ active: route.path === '/' }"><AppIcon name="dashboard" />ダッシュボード</NuxtLink>
        <NuxtLink to="/clients" :class="{ active: route.path.startsWith('/clients') }"><AppIcon name="clients" />クライアント</NuxtLink>
      </nav>
      <NuxtLink to="/clients/new" class="button button-primary header-action"><AppIcon name="plus" />新規登録</NuxtLink>
    </div>
  </header>
</template>

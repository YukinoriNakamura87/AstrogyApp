<script setup lang="ts">
import type { ClientListResponse } from '~/types/client'

useHead({ title: 'クライアント一覧 | Astrolabe' })

const search = ref('')
const sign = ref('')
const appliedSearch = ref('')
const query = computed(() => ({ search: appliedSearch.value || undefined, sign: sign.value || undefined }))
const { data, status, error, refresh } = await useFetch<ClientListResponse>('/api/clients', { query })

const signs = [
  ['', 'すべてのサイン'], ['Ari', '牡羊座'], ['Tau', '牡牛座'], ['Gem', '双子座'],
  ['Can', '蟹座'], ['Leo', '獅子座'], ['Vir', '乙女座'], ['Lib', '天秤座'],
  ['Sco', '蠍座'], ['Sag', '射手座'], ['Cap', '山羊座'], ['Aqu', '水瓶座'], ['Pis', '魚座'],
]

function submitSearch() {
  appliedSearch.value = search.value.trim()
}

function clearFilters() {
  search.value = ''
  appliedSearch.value = ''
  sign.value = ''
}
</script>

<template>
  <main class="page-container clients-page">
    <section class="page-heading split-heading">
      <div><p class="eyebrow">CLIENTS</p><h1>クライアント</h1><p class="heading-copy">出生情報とチャートを一か所で管理します。</p></div>
      <NuxtLink to="/clients/new" class="button button-primary"><AppIcon name="plus" />新規クライアント</NuxtLink>
    </section>

    <section class="content-panel filter-panel" aria-label="クライアント検索">
      <form class="search-box" @submit.prevent="submitSearch">
        <AppIcon name="search" />
        <input v-model="search" type="search" placeholder="名前・出生地で検索" aria-label="名前または出生地で検索">
        <button type="submit">検索</button>
      </form>
      <label class="select-wrap">
        <span>サインで絞り込み</span>
        <select v-model="sign">
          <option v-for="item in signs" :key="item[0]" :value="item[0]">{{ item[1] }}</option>
        </select>
      </label>
    </section>

    <div class="list-meta">
      <p><strong>{{ data?.total ?? 0 }}</strong> 名のクライアント</p>
      <button v-if="appliedSearch || sign" class="clear-button" @click="clearFilters">絞り込みを解除</button>
    </div>

    <div v-if="status === 'pending'" class="loading-panel"><span class="spinner" />クライアントを読み込んでいます</div>
    <div v-else-if="error" class="error-panel"><p>クライアント一覧を読み込めませんでした。</p><button class="button button-secondary" @click="refresh()">再読み込み</button></div>
    <section v-else-if="data?.items.length" class="content-panel client-list full-list">
      <ClientRow v-for="client in data.items" :key="client.id" :client="client" />
    </section>
    <section v-else class="content-panel empty-state large-empty">
      <span class="empty-symbol">✦</span>
      <h2>{{ appliedSearch || sign ? '条件に合うクライアントはいません' : 'クライアントはまだ登録されていません' }}</h2>
      <p>{{ appliedSearch || sign ? '検索条件を変えて、もう一度お試しください。' : '最初のクライアントを登録して、チャートを作成しましょう。' }}</p>
      <button v-if="appliedSearch || sign" class="button button-secondary" @click="clearFilters">絞り込みを解除</button>
      <NuxtLink v-else to="/clients/new" class="button button-primary"><AppIcon name="plus" />クライアントを登録</NuxtLink>
    </section>
  </main>
</template>

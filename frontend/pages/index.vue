<script setup lang="ts">
import type { DashboardResponse } from '~/types/client'

useHead({ title: 'ダッシュボード | Astrolabe' })

const { data, status, error, refresh } = await useFetch<DashboardResponse>('/api/dashboard')
const today = new Intl.DateTimeFormat('ja-JP', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }).format(new Date())
</script>

<template>
  <main class="page-container dashboard-page">
    <section class="page-heading dashboard-heading">
      <div>
        <p class="eyebrow">OVERVIEW</p>
        <h1>ダッシュボード</h1>
        <p class="heading-copy">今日のリーディングを、ここから始めましょう。</p>
      </div>
      <p class="today">{{ today }}</p>
    </section>

    <div v-if="status === 'pending'" class="loading-panel"><span class="spinner" />データを読み込んでいます</div>
    <div v-else-if="error" class="error-panel">
      <p>ダッシュボードを読み込めませんでした。</p>
      <button class="button button-secondary" @click="refresh()">再読み込み</button>
    </div>

    <template v-else-if="data">
      <section class="stats-grid" aria-label="利用状況">
        <article class="stat-card">
          <span class="stat-icon"><AppIcon name="clients" /></span>
          <div><p>登録クライアント</p><strong>{{ data.client_count }}</strong><small>名</small></div>
        </article>
        <article class="stat-card">
          <span class="stat-icon"><AppIcon name="chart" /></span>
          <div><p>作成済みチャート</p><strong>{{ data.chart_count }}</strong><small>件</small></div>
        </article>
        <article class="stat-card muted-stat">
          <span class="stat-icon"><AppIcon name="sessions" /></span>
          <div><p>セッション記録</p><strong>{{ data.session_count }}</strong><small>件</small></div>
          <span class="coming-soon">準備中</span>
        </article>
      </section>

      <section class="dashboard-grid">
        <div class="content-panel recent-panel">
          <div class="panel-heading">
            <div><p class="eyebrow">RECENT CLIENTS</p><h2>最近のクライアント</h2></div>
            <NuxtLink to="/clients" class="text-link">すべて見る <AppIcon name="arrow" /></NuxtLink>
          </div>
          <div v-if="data.recent_clients.length" class="client-list">
            <ClientRow v-for="client in data.recent_clients" :key="client.id" :client="client" compact />
          </div>
          <div v-else class="empty-state">
            <span class="empty-symbol">☉</span>
            <h3>最初のクライアントを登録しましょう</h3>
            <p>出生情報を登録すると、ネイタルチャートを作成できます。</p>
            <NuxtLink to="/clients/new" class="button button-primary"><AppIcon name="plus" />クライアントを登録</NuxtLink>
          </div>
        </div>

        <aside class="side-stack">
          <div class="content-panel quick-panel">
            <p class="eyebrow">QUICK START</p>
            <h2>新しいリーディング</h2>
            <p>クライアント情報を登録し、ネイタルチャートを準備します。</p>
            <NuxtLink to="/clients/new" class="button button-primary button-wide"><AppIcon name="plus" />新規クライアント登録</NuxtLink>
          </div>
          <div class="content-panel session-preview">
            <div class="panel-heading"><div><p class="eyebrow">SESSIONS</p><h2>最近のセッション</h2></div></div>
            <div class="soft-empty"><AppIcon name="sessions" /><p>セッション機能は<br>次のフェーズで追加されます</p></div>
          </div>
        </aside>
      </section>
    </template>
  </main>
</template>

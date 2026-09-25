<script setup lang="ts">
import type { ClientProfileResponse, LillyScoreResponse } from '~/types/client'

type ChartPoint = {
  name: string
  sign: string
  emoji?: string
  house?: string | null
  position: number
  abs_pos?: number
  element?: string
  quality?: string
  retrograde?: boolean | null
  point_type: string
}

type ChartAspect = {
  p1_name: string
  p2_name: string
  aspect: string
  orbit: number
  aspect_movement?: string
}

const route = useRoute()
const clientId = String(route.params.id)
const { data, status, error, refresh } = await useFetch<ClientProfileResponse>(`/api/clients/${clientId}`)
const { data: lillyScore, status: lillyStatus, error: lillyError } = await useFetch<LillyScoreResponse>(`/api/clients/${clientId}/chart/lilly-score`)
const calculating = ref(false)
const calculationError = ref('')
const exporting = ref(false)
const exportNotice = ref('')

useHead({ title: computed(() => data.value ? `${data.value.client.name} | Astrolabe` : 'クライアント詳細 | Astrolabe') })

const signLabels: Record<string, string> = {
  Ari: '牡羊座', Tau: '牡牛座', Gem: '双子座', Can: '蟹座', Leo: '獅子座', Vir: '乙女座',
  Lib: '天秤座', Sco: '蠍座', Sag: '射手座', Cap: '山羊座', Aqu: '水瓶座', Pis: '魚座',
}
const pointLabels: Record<string, string> = {
  Sun: '太陽', Moon: '月', Mercury: '水星', Venus: '金星', Mars: '火星', Jupiter: '木星',
  Saturn: '土星', Uranus: '天王星', Neptune: '海王星', Pluto: '冥王星', Chiron: 'キロン',
  True_North_Lunar_Node: 'ドラゴンヘッド', Ascendant: 'ASC', Medium_Coeli: 'MC',
}
const houseLabels: Record<string, string> = {
  First_House: '第1ハウス', Second_House: '第2ハウス', Third_House: '第3ハウス', Fourth_House: '第4ハウス',
  Fifth_House: '第5ハウス', Sixth_House: '第6ハウス', Seventh_House: '第7ハウス', Eighth_House: '第8ハウス',
  Ninth_House: '第9ハウス', Tenth_House: '第10ハウス', Eleventh_House: '第11ハウス', Twelfth_House: '第12ハウス',
}
const aspectLabels: Record<string, string> = {
  conjunction: 'コンジャンクション', opposition: 'オポジション', trine: 'トライン',
  square: 'スクエア', sextile: 'セクスタイル', quincunx: 'クインカンクス',
  semisextile: 'セミセクスタイル', semisquare: 'セミスクエア', sesquiquadrate: 'セスキコードレイト',
}
const aspectSymbols: Record<string, string> = { conjunction: '☌', opposition: '☍', trine: '△', square: '□', sextile: '⚹', quincunx: '⚻' }
const elementLabels: Record<string, string> = { fire: '火', earth: '地', air: '風', water: '水' }
const qualityLabels: Record<string, string> = { cardinal: '活動', fixed: '不動', mutable: '柔軟' }
const primaryOrder = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron', 'True_North_Lunar_Node']
const houseOrder = Object.keys(houseLabels)
const aspectPointNames = new Set([...primaryOrder, 'Ascendant', 'Medium_Coeli'])

const subject = computed(() => (data.value?.chart?.calculation.subject || {}) as Record<string, unknown>)
const allPoints = computed(() => Object.values(subject.value).filter((item): item is ChartPoint => !!item && typeof item === 'object' && 'point_type' in item))
const pointByName = computed(() => new Map(allPoints.value.map(point => [point.name, point])))
const primaryPoints = computed(() => primaryOrder.map(name => pointByName.value.get(name)).filter((point): point is ChartPoint => !!point))
const houses = computed(() => houseOrder.map(name => pointByName.value.get(name)).filter((point): point is ChartPoint => !!point))
const majorAspects = computed(() => ((data.value?.chart?.calculation.aspects || []) as unknown as ChartAspect[])
  .filter(aspect => aspectPointNames.has(aspect.p1_name) && aspectPointNames.has(aspect.p2_name))
  .sort((a, b) => a.orbit - b.orbit))
const bigThree = computed(() => [pointByName.value.get('Sun'), pointByName.value.get('Moon'), pointByName.value.get('Ascendant')].filter((point): point is ChartPoint => !!point))
const elementDistribution = computed(() => data.value?.chart?.calculation.element_distribution || {})
const qualityDistribution = computed(() => data.value?.chart?.calculation.quality_distribution || {})

const sign = (value: string) => signLabels[value] || value
const pointName = (value: string) => pointLabels[value] || value.replaceAll('_', ' ')
const house = (value: string | null | undefined) => value ? houseLabels[value] || value.replaceAll('_', ' ') : '—'
const degree = (value: number) => `${Math.floor(value)}° ${String(Math.floor((value % 1) * 60)).padStart(2, '0')}′`
const signedScore = (value: number) => value > 0 ? `+${value}` : String(value)
const date = (value: string) => new Intl.DateTimeFormat('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' }).format(new Date(`${value}T00:00:00`))
const time = (value: string | null) => value ? value.slice(0, 5) : '不明'

async function calculateChart() {
  calculationError.value = ''
  calculating.value = true
  try {
    await $fetch(`/api/clients/${clientId}/chart`)
    await refresh()
  } catch (err: any) {
    calculationError.value = err?.data?.data?.detail || 'チャートを作成できませんでした。'
  } finally {
    calculating.value = false
  }
}

async function fetchChartSummary() {
  return await $fetch<string>(`/api/clients/${clientId}/chart/summary`)
}

async function downloadSummary() {
  exporting.value = true
  exportNotice.value = ''
  try {
    const markdown = await fetchChartSummary()
    const url = URL.createObjectURL(new Blob([markdown], { type: 'text/markdown;charset=utf-8' }))
    const anchor = document.createElement('a')
    const safeName = data.value?.client.name.replace(/[\\/:*?"<>|]/g, '_') || `client-${clientId}`
    anchor.href = url
    anchor.download = `${safeName}-natal-chart.md`
    anchor.click()
    URL.revokeObjectURL(url)
    exportNotice.value = 'Markdownファイルをダウンロードしました。'
  } catch {
    exportNotice.value = 'まとめテキストを出力できませんでした。'
  } finally {
    exporting.value = false
  }
}

async function copySummary() {
  exporting.value = true
  exportNotice.value = ''
  try {
    await navigator.clipboard.writeText(await fetchChartSummary())
    exportNotice.value = 'まとめテキストをコピーしました。'
  } catch {
    exportNotice.value = 'クリップボードへコピーできませんでした。'
  } finally {
    exporting.value = false
  }
}
</script>

<template>
  <main class="page-container profile-page">
    <div v-if="status === 'pending'" class="loading-panel"><span class="spinner" />クライアント情報を読み込んでいます</div>
    <section v-else-if="error" class="content-panel empty-state large-empty">
      <span class="empty-symbol">!</span><h1>クライアントが見つかりません</h1><p>削除されたか、URLが正しくない可能性があります。</p><NuxtLink to="/clients" class="button button-secondary">一覧へ戻る</NuxtLink>
    </section>

    <template v-else-if="data">
      <NuxtLink to="/clients" class="back-link"><AppIcon name="arrow" />クライアント一覧</NuxtLink>
      <section class="profile-hero">
        <div class="profile-avatar">{{ data.client.name.slice(0, 1) }}</div>
        <div class="profile-title"><p class="eyebrow">CLIENT PROFILE</p><h1>{{ data.client.name }}</h1><p>{{ date(data.client.birth_date) }} · {{ time(data.client.birth_time) }} · {{ data.client.birth_place }}</p></div>
        <span class="profile-id">CLIENT #{{ data.client.id }}</span>
      </section>

      <section v-if="data.chart && bigThree.length" class="big-three-grid" aria-label="主要3天体">
        <article v-for="point in bigThree" :key="point.name" class="big-three-card">
          <span class="zodiac-glyph">{{ point.emoji || '✦' }}</span>
          <div><small>{{ pointName(point.name) }}</small><strong>{{ sign(point.sign) }}</strong><p>{{ degree(point.position) }} · {{ house(point.house) }}</p></div>
        </article>
      </section>

      <section class="profile-layout">
        <div class="profile-main">
          <div class="content-panel detail-section">
            <div class="panel-heading"><div><p class="eyebrow">BIRTH DATA</p><h2>出生情報</h2></div></div>
            <dl class="birth-data-grid">
              <div><dt>生年月日</dt><dd>{{ date(data.client.birth_date) }}</dd></div>
              <div><dt>出生時刻</dt><dd>{{ time(data.client.birth_time) }}</dd></div>
              <div class="wide"><dt>出生地</dt><dd>{{ data.client.birth_place }}</dd></div>
              <div><dt>緯度・経度</dt><dd>{{ data.client.birth_latitude }}, {{ data.client.birth_longitude }}</dd></div>
              <div><dt>タイムゾーン</dt><dd>{{ data.client.birth_timezone }}</dd></div>
            </dl>
          </div>

          <template v-if="data.chart">
            <div class="content-panel chart-export-panel">
              <div><p class="eyebrow">CHART SUMMARY</p><h2>チャート情報のまとめ</h2><p>度分秒・在室ハウスを含むMarkdown形式で、AIへの共有にも使えます。</p><small v-if="exportNotice" role="status">{{ exportNotice }}</small></div>
              <div class="chart-export-actions"><button class="button button-secondary" :disabled="exporting" @click="copySummary">コピー</button><button class="button button-primary" :disabled="exporting" @click="downloadSummary"><span v-if="exporting" class="spinner" />Markdown出力</button></div>
            </div>

            <div class="content-panel detail-section lilly-panel">
              <div class="panel-heading"><div><p class="eyebrow">LILLY SCORE</p><h2>リリー式採点</h2></div><span v-if="lillyScore" class="sect-badge">{{ lillyScore.sect === 'day' ? '昼チャート' : '夜チャート' }}</span></div>
              <div v-if="lillyStatus === 'pending'" class="lilly-loading"><span class="spinner" />採点しています</div>
              <div v-else-if="lillyError || !lillyScore" class="lilly-error">採点結果を取得できませんでした。</div>
              <template v-else>
                <div class="lilly-totals">
                  <div><small>エッセンシャル</small><strong :class="{ negative: lillyScore.essential_total < 0 }">{{ signedScore(lillyScore.essential_total) }}</strong></div>
                  <div><small>アクシデンタル</small><strong :class="{ negative: lillyScore.accidental_total < 0 }">{{ signedScore(lillyScore.accidental_total) }}</strong></div>
                  <div class="grand"><small>総合</small><strong :class="{ negative: lillyScore.grand_total < 0 }">{{ signedScore(lillyScore.grand_total) }}</strong></div>
                </div>
                <p v-for="warning in lillyScore.warnings" :key="warning" class="lilly-warning">{{ warning }}</p>
                <div class="lilly-planet-list">
                  <details v-for="planet in lillyScore.planets" :key="planet.planet">
                    <summary><strong>{{ pointName(planet.planet) }}</strong><span><small>本質</small>{{ signedScore(planet.essential.total) }}</span><span><small>偶発</small>{{ signedScore(planet.accidental.total) }}</span><b :class="{ negative: planet.total < 0 }">{{ signedScore(planet.total) }}</b></summary>
                    <div class="lilly-breakdown">
                      <section><h3>エッセンシャル <span>{{ signedScore(planet.essential.total) }}</span></h3><ul><li v-for="item in planet.essential.items" :key="`${planet.planet}-e-${item.code}-${item.related_body}`" :class="item.status"><div><strong>{{ item.label }}</strong><small>{{ item.description }}</small></div><b :class="{ negative: item.points < 0 }">{{ signedScore(item.points) }}</b></li></ul></section>
                      <section><h3>アクシデンタル <span>{{ signedScore(planet.accidental.total) }}</span></h3><ul><li v-for="item in planet.accidental.items" :key="`${planet.planet}-a-${item.code}-${item.related_body}`" :class="item.status"><div><strong>{{ item.label }}</strong><small>{{ item.description }}</small></div><b :class="{ negative: item.points < 0 }">{{ signedScore(item.points) }}</b></li></ul></section>
                    </div>
                  </details>
                </div>
              </template>
            </div>

            <div class="content-panel detail-section">
              <div class="panel-heading"><div><p class="eyebrow">PLANETS</p><h2>主要天体</h2></div><span class="result-count">Kerykeion {{ data.chart.calculation_version }}</span></div>
              <div class="detail-table-wrap"><table class="detail-table"><thead><tr><th>天体</th><th>サイン</th><th>度数</th><th>ハウス</th><th>状態</th></tr></thead><tbody>
                <tr v-for="point in primaryPoints" :key="point.name"><td><span class="table-glyph">{{ point.emoji }}</span>{{ pointName(point.name) }}</td><td>{{ sign(point.sign) }}</td><td>{{ degree(point.position) }}</td><td>{{ house(point.house) }}</td><td><span v-if="point.retrograde" class="retrograde">逆行</span><span v-else>順行</span></td></tr>
              </tbody></table></div>
            </div>

            <div class="content-panel detail-section">
              <div class="panel-heading"><div><p class="eyebrow">HOUSES</p><h2>ハウスカスプ</h2></div></div>
              <div class="house-grid"><article v-for="item in houses" :key="item.name"><small>{{ house(item.name) }}</small><strong>{{ item.emoji }} {{ sign(item.sign) }}</strong><span>{{ degree(item.position) }}</span></article></div>
            </div>

            <div class="content-panel detail-section">
              <div class="panel-heading"><div><p class="eyebrow">ASPECTS</p><h2>主要アスペクト</h2></div><span class="result-count">{{ majorAspects.length }}件</span></div>
              <div class="aspect-list">
                <article v-for="(aspect, index) in majorAspects" :key="`${aspect.p1_name}-${aspect.p2_name}-${index}`">
                  <span>{{ pointName(aspect.p1_name) }}</span><strong class="aspect-symbol">{{ aspectSymbols[aspect.aspect] || '·' }}</strong><span>{{ pointName(aspect.p2_name) }}</span><small>{{ aspectLabels[aspect.aspect] || aspect.aspect }} · オーブ {{ aspect.orbit.toFixed(2) }}° · {{ aspect.aspect_movement === 'Applying' ? '接近' : '分離' }}</small>
                </article>
              </div>
            </div>
          </template>

          <div v-else class="content-panel no-chart-panel">
            <span class="empty-symbol">☉</span><div><h2>チャートがまだありません</h2><p>保存済みの出生情報からネイタルチャートを計算します。</p><p v-if="calculationError" class="inline-error">{{ calculationError }}</p></div><button class="button button-primary" :disabled="calculating" @click="calculateChart"><span v-if="calculating" class="spinner" />{{ calculating ? '計算中' : 'チャートを作成' }}</button>
          </div>

          <div class="content-panel detail-section">
            <div class="panel-heading"><div><p class="eyebrow">SESSIONS</p><h2>セッション履歴</h2></div><span class="coming-soon static">準備中</span></div>
            <div class="soft-empty profile-empty"><AppIcon name="sessions" /><p>セッション記録はまだありません<br>この機能は次のフェーズで追加されます</p></div>
          </div>
        </div>

        <aside v-if="data.chart" class="profile-sidebar">
          <div class="content-panel distribution-panel">
            <p class="eyebrow">ELEMENTS</p><h2>四元素</h2>
            <div class="distribution-list"><div v-for="key in ['fire', 'earth', 'air', 'water']" :key="key"><span>{{ elementLabels[key] }}</span><div><i :style="{ width: `${elementDistribution[`${key}_percentage`] || 0}%` }" /></div><strong>{{ elementDistribution[`${key}_percentage`] || 0 }}%</strong></div></div>
          </div>
          <div class="content-panel distribution-panel">
            <p class="eyebrow">QUALITIES</p><h2>三区分</h2>
            <div class="distribution-list"><div v-for="key in ['cardinal', 'fixed', 'mutable']" :key="key"><span>{{ qualityLabels[key] }}</span><div><i :style="{ width: `${qualityDistribution[`${key}_percentage`] || 0}%` }" /></div><strong>{{ qualityDistribution[`${key}_percentage`] || 0 }}%</strong></div></div>
          </div>
        </aside>
      </section>
    </template>
  </main>
</template>

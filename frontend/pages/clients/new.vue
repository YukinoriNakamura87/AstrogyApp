<script setup lang="ts">
type Point = { name: string; point_type: string; sign?: string; position?: number; house?: string | null; retrograde?: boolean | null }
type Aspect = { p1_name: string; p2_name: string; aspect: string; orbit: number }
type Chart = { client_id: number; calculation_version: string; calculation: { subject: Record<string, unknown>; aspects: Aspect[]; [key: string]: unknown } }
type BirthPlace = {
  id: string
  name: string
  display_name: string
  admin1: string | null
  admin2: string | null
  country: string
  country_code: string
  latitude: string
  longitude: string
  timezone: string
}

useHead({ title: 'クライアント登録 | Astrolabe' })

const form = reactive({ name: '', birth_date: '', birth_time: '', birth_place: '', birth_latitude: '', birth_longitude: '', birth_timezone: '' })
const locationQuery = ref('')
const selectedLocation = ref<BirthPlace | null>(null)
const locationResults = ref<BirthPlace[]>([])
const locationError = ref('')
const searchingLocation = ref(false)
const manualLocation = ref(false)
const chart = ref<Chart | null>(null)
const errorMessage = ref('')
const loading = ref(false)
const points = computed(() => Object.values(chart.value?.calculation.subject || {}).filter((value): value is Point => !!value && typeof value === 'object' && 'point_type' in value && value.point_type === 'AstrologicalPoint'))
const houses = computed(() => Object.values(chart.value?.calculation.subject || {}).filter((value): value is Point => !!value && typeof value === 'object' && 'point_type' in value && value.point_type === 'House'))

watch(locationQuery, (value) => {
  if (selectedLocation.value && value !== selectedLocation.value.display_name) {
    selectedLocation.value = null
    form.birth_place = ''
    form.birth_latitude = ''
    form.birth_longitude = ''
    form.birth_timezone = ''
  }
})

function readableError(error: any): string {
  const detail = error?.data?.data?.detail || error?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map(item => `${item.loc?.join('.')}: ${item.msg}`).join(' / ')
  return error?.message || '通信に失敗しました。'
}

async function searchLocations() {
  locationError.value = ''
  locationResults.value = []
  const query = locationQuery.value.trim()
  if (query.length < 2) {
    locationError.value = '出生地はローマ字2文字以上で入力してください。'
    return
  }
  searchingLocation.value = true
  try {
    const response = await $fetch<{ items: BirthPlace[] }>('/api/locations/search', { query: { q: query } })
    locationResults.value = response.items
    if (!response.items.length) locationError.value = '候補が見つかりませんでした。市区町村名を変えてお試しください。'
  } catch (error) {
    locationError.value = readableError(error)
  } finally {
    searchingLocation.value = false
  }
}

function chooseLocation(place: BirthPlace) {
  selectedLocation.value = place
  locationQuery.value = place.display_name
  form.birth_place = place.display_name
  form.birth_latitude = String(place.latitude)
  form.birth_longitude = String(place.longitude)
  form.birth_timezone = place.timezone
  locationResults.value = []
  locationError.value = ''
}

function enableManualLocation() {
  manualLocation.value = !manualLocation.value
  if (manualLocation.value && !form.birth_place) form.birth_place = locationQuery.value.trim()
}

async function calculate() {
  errorMessage.value = ''
  chart.value = null
  if (!form.birth_latitude || !form.birth_longitude || !form.birth_timezone) {
    errorMessage.value = '出生地を検索して候補を選択するか、詳細設定から位置情報を入力してください。'
    return
  }
  loading.value = true
  try {
    const client = await $fetch<{ id: number }>('/api/clients', {
      method: 'POST',
      body: { ...form, birth_latitude: Number(form.birth_latitude), birth_longitude: Number(form.birth_longitude), birth_time: form.birth_time ? `${form.birth_time}:00` : null },
    })
    chart.value = await $fetch<Chart>(`/api/clients/${client.id}/chart`)
  } catch (error) {
    errorMessage.value = readableError(error)
  } finally {
    loading.value = false
  }
}

const formatted = (value: number | null | undefined) => typeof value === 'number' ? value.toFixed(2) : '—'
</script>

<template>
  <main class="page-container register-page">
    <section class="page-heading split-heading">
      <div><p class="eyebrow">NEW CLIENT</p><h1>クライアント登録</h1><p class="heading-copy">出生情報を登録し、ネイタルチャートを作成します。</p></div>
      <NuxtLink to="/clients" class="button button-secondary">一覧へ戻る</NuxtLink>
    </section>

    <section class="content-panel form-panel">
      <div class="section-title"><span>01</span><div><h2>基本情報・出生情報</h2><p>出生地を検索すると、チャート計算に必要な座標とタイムゾーンが自動入力されます。</p></div></div>
      <form class="form-grid" @submit.prevent="calculate">
        <label class="field field-wide"><span>お名前</span><input v-model.trim="form.name" name="name" required maxlength="200" autocomplete="name" placeholder="例：山田 花子"></label>
        <label class="field"><span>生年月日</span><input v-model="form.birth_date" name="birth_date" required type="date"></label>
        <label class="field"><span>出生時刻</span><input v-model="form.birth_time" name="birth_time" required type="time"><small>不明な場合は登録後のチャート計算ができません</small></label>

        <div class="field field-wide location-field">
          <span>出生地 <small>（ローマ字）</small></span>
          <div class="location-search">
            <input v-model="locationQuery" required maxlength="200" placeholder="例：Moriyama, Shiga" autocomplete="off" @keydown.enter.prevent="searchLocations">
            <button type="button" class="button button-secondary" :disabled="searchingLocation" @click="searchLocations">
              <span v-if="searchingLocation" class="spinner" />{{ searchingLocation ? '検索中' : '検索' }}
            </button>
          </div>
          <p v-if="locationError" class="location-error" role="alert">{{ locationError }}</p>
          <div v-if="locationResults.length" class="location-results" role="listbox" aria-label="出生地の検索候補">
            <button v-for="place in locationResults" :key="place.id" type="button" role="option" @click="chooseLocation(place)">
              <span class="place-pin">⌖</span>
              <span class="place-copy"><strong>{{ place.display_name }}</strong><small>{{ place.latitude }}, {{ place.longitude }} · {{ place.timezone }}</small></span>
              <span class="choose-label">選択</span>
            </button>
          </div>
          <div v-if="selectedLocation" class="selected-location">
            <span class="selected-check">✓</span>
            <span><strong>{{ selectedLocation.display_name }}</strong><small>緯度 {{ selectedLocation.latitude }} / 経度 {{ selectedLocation.longitude }} / {{ selectedLocation.timezone }}</small></span>
          </div>
          <div class="location-help">
            <small>位置情報：</small><a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo / GeoNames</a>
            <button type="button" @click="enableManualLocation">{{ manualLocation ? '詳細設定を閉じる' : '座標を手動入力' }}</button>
          </div>
        </div>

        <div v-if="manualLocation" class="manual-location field-wide">
          <label class="field field-wide"><span>保存する出生地名</span><input v-model.trim="form.birth_place" required maxlength="255" placeholder="例：滋賀県守山市"></label>
          <label class="field"><span>緯度</span><input v-model="form.birth_latitude" required type="number" step="0.000001" min="-90" max="90" placeholder="35.0589"></label>
          <label class="field"><span>経度</span><input v-model="form.birth_longitude" required type="number" step="0.000001" min="-180" max="180" placeholder="135.9944"></label>
          <label class="field field-wide"><span>タイムゾーン</span><input v-model.trim="form.birth_timezone" required placeholder="Asia/Tokyo"></label>
        </div>

        <div class="form-footer field-wide">
          <p v-if="errorMessage" class="inline-error" role="alert">{{ errorMessage }}</p>
          <button type="submit" class="button button-primary submit-button" :disabled="loading"><span v-if="loading" class="spinner" />{{ loading ? '計算しています' : '登録してチャートを作成' }}</button>
        </div>
      </form>
    </section>

    <template v-if="chart">
      <section class="success-banner"><span>✓</span><div><strong>クライアントとチャートを登録しました</strong><p>クライアントID {{ chart.client_id }} · Kerykeion {{ chart.calculation_version }}</p></div></section>
      <section class="content-panel chart-results">
        <div class="panel-heading"><div><p class="eyebrow">NATAL CHART</p><h2>チャート計算結果</h2></div><span class="result-count">天体 {{ points.length }} · ハウス {{ houses.length }} · アスペクト {{ chart.calculation.aspects.length }}</span></div>
        <div class="result-tabs">
          <div><h3>天体・感受点</h3><div class="table-wrap"><table><thead><tr><th>天体</th><th>サイン</th><th>度数</th><th>ハウス</th><th>逆行</th></tr></thead><tbody><tr v-for="point in points" :key="point.name"><td>{{ point.name }}</td><td>{{ point.sign || '—' }}</td><td>{{ formatted(point.position) }}</td><td>{{ point.house || '—' }}</td><td>{{ point.retrograde ? 'R' : '—' }}</td></tr></tbody></table></div></div>
          <div><h3>ハウス</h3><div class="table-wrap"><table><thead><tr><th>カスプ</th><th>サイン</th><th>度数</th></tr></thead><tbody><tr v-for="house in houses" :key="house.name"><td>{{ house.name }}</td><td>{{ house.sign || '—' }}</td><td>{{ formatted(house.position) }}</td></tr></tbody></table></div></div>
        </div>
        <details class="raw-json"><summary>計算結果のJSONを表示</summary><pre>{{ JSON.stringify(chart, null, 2) }}</pre></details>
      </section>
    </template>
  </main>
</template>

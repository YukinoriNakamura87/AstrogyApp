<script setup lang="ts">
import { formatDegreeMinutes } from '~/utils/angle'

type RawPoint = {
  name: string
  sign: string
  position: number
  abs_pos: number
  retrograde?: boolean | null
  point_type: string
}

type RawAspect = {
  p1_name: string
  p2_name: string
  aspect: string
  orbit: number
}

type Calculation = {
  subject?: Record<string, unknown>
  aspects?: Array<Record<string, unknown>>
}

const props = defineProps<{ calculation: Calculation }>()
const showAspects = ref(true)

const size = 720
const center = size / 2
const outerRadius = 326
const zodiacInnerRadius = 266
const aspectRadius = 139

const signs = [
  { key: 'Ari', glyph: '♈', label: '牡羊座' }, { key: 'Tau', glyph: '♉', label: '牡牛座' },
  { key: 'Gem', glyph: '♊', label: '双子座' }, { key: 'Can', glyph: '♋', label: '蟹座' },
  { key: 'Leo', glyph: '♌', label: '獅子座' }, { key: 'Vir', glyph: '♍', label: '乙女座' },
  { key: 'Lib', glyph: '♎', label: '天秤座' }, { key: 'Sco', glyph: '♏', label: '蠍座' },
  { key: 'Sag', glyph: '♐', label: '射手座' }, { key: 'Cap', glyph: '♑', label: '山羊座' },
  { key: 'Aqu', glyph: '♒', label: '水瓶座' }, { key: 'Pis', glyph: '♓', label: '魚座' },
]

const houseNames = [
  'First_House', 'Second_House', 'Third_House', 'Fourth_House', 'Fifth_House', 'Sixth_House',
  'Seventh_House', 'Eighth_House', 'Ninth_House', 'Tenth_House', 'Eleventh_House', 'Twelfth_House',
]

const displayedNames = [
  'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus',
  'Neptune', 'Pluto', 'Chiron', 'True_North_Lunar_Node', 'Ascendant', 'Medium_Coeli',
]

const glyphs: Record<string, string> = {
  Sun: '☉', Moon: '☽', Mercury: '☿', Venus: '♀', Mars: '♂', Jupiter: '♃', Saturn: '♄',
  Uranus: '♅', Neptune: '♆', Pluto: '♇', Chiron: '⚷', True_North_Lunar_Node: '☊',
  Ascendant: 'ASC', Medium_Coeli: 'MC',
}

const names: Record<string, string> = {
  Sun: '太陽', Moon: '月', Mercury: '水星', Venus: '金星', Mars: '火星', Jupiter: '木星',
  Saturn: '土星', Uranus: '天王星', Neptune: '海王星', Pluto: '冥王星', Chiron: 'キロン',
  True_North_Lunar_Node: 'ドラゴンヘッド', Ascendant: 'ASC', Medium_Coeli: 'MC',
}

const planetColors: Record<string, string> = {
  Sun: '#f2ca68', Moon: '#dce4f1', Mercury: '#b6c7d9', Venus: '#db9eae', Mars: '#df8179',
  Jupiter: '#d9b078', Saturn: '#a8a496', Uranus: '#83c6ca', Neptune: '#779ed5', Pluto: '#b68bbf',
  Chiron: '#9da9bb', True_North_Lunar_Node: '#d7b45d', Ascendant: '#efd07d', Medium_Coeli: '#efd07d',
}

const aspectStyles: Record<string, { color: string; dash?: string }> = {
  conjunction: { color: '#d7b45d' }, opposition: { color: '#d97979' }, square: { color: '#d97979', dash: '5 4' },
  trine: { color: '#72a9d8' }, sextile: { color: '#77b99d', dash: '3 3' },
}

const allPoints = computed<RawPoint[]>(() => Object.values(props.calculation.subject || {})
  .filter((value): value is RawPoint => !!value && typeof value === 'object' && 'point_type' in value && 'abs_pos' in value))
const byName = computed<Map<string, RawPoint>>(() => new Map(allPoints.value.map((point: RawPoint) => [point.name, point])))
const ascendant = computed(() => byName.value.get('Ascendant')?.abs_pos ?? 0)
const houses = computed<RawPoint[]>(() => houseNames.map(name => byName.value.get(name)).filter((point): point is RawPoint => !!point))

const normalize = (value: number) => ((value % 360) + 360) % 360
const screenAngle = (longitude: number) => 180 - normalize(longitude - ascendant.value)
const pointAt = (longitude: number, radius: number) => {
  const radians = screenAngle(longitude) * Math.PI / 180
  return { x: center + Math.cos(radians) * radius, y: center + Math.sin(radians) * radius }
}

const ticks = Array.from({ length: 72 }, (_, index) => ({ longitude: index * 5, major: index % 6 === 0 }))

const planetPositions = computed(() => {
  const ordered = displayedNames
    .map(name => byName.value.get(name))
    .filter((point): point is RawPoint => !!point)
    .sort((a, b) => normalize(a.abs_pos - ascendant.value) - normalize(b.abs_pos - ascendant.value))
  const lanes = [226, 203, 180]
  let previousAngle = -100
  let lane = 0
  return ordered.map(point => {
    const angle = normalize(point.abs_pos - ascendant.value)
    lane = angle - previousAngle < 9 ? (lane + 1) % lanes.length : 0
    previousAngle = angle
    return {
      ...point,
      glyph: glyphs[point.name] || '•',
      label: names[point.name] || point.name,
      color: planetColors[point.name] || '#dce4f1',
      anchor: pointAt(point.abs_pos, zodiacInnerRadius - 2),
      connector: pointAt(point.abs_pos, lanes[lane] + 15),
      labelPosition: pointAt(point.abs_pos, lanes[lane]),
    }
  })
})

const aspectPointNames = computed(() => new Set(planetPositions.value.map((point: RawPoint) => point.name)))
const aspects = computed(() => ((props.calculation.aspects || []) as unknown as RawAspect[])
  .filter(aspect => aspectStyles[aspect.aspect] && aspectPointNames.value.has(aspect.p1_name) && aspectPointNames.value.has(aspect.p2_name))
  .map(aspect => {
    const first = byName.value.get(aspect.p1_name)!
    const second = byName.value.get(aspect.p2_name)!
    return {
      ...aspect,
      from: pointAt(first.abs_pos, aspectRadius),
      to: pointAt(second.abs_pos, aspectRadius),
      style: aspectStyles[aspect.aspect],
      opacity: Math.max(.2, .72 - aspect.orbit * .045),
    }
  }))

const houseLines = computed(() => houses.value.map((house: RawPoint, index: number) => ({
  number: index + 1,
  longitude: house.abs_pos,
  outer: pointAt(house.abs_pos, zodiacInnerRadius),
  inner: pointAt(house.abs_pos, 26),
  angular: [0, 3, 6, 9].includes(index),
})))

const houseLabels = computed(() => houses.value.map((house: RawPoint, index: number) => {
  const next = houses.value[(index + 1) % houses.value.length]
  const span = normalize(next.abs_pos - house.abs_pos)
  return { number: index + 1, position: pointAt(house.abs_pos + span / 2, 109) }
}))

</script>

<template>
  <section class="content-panel natal-wheel-panel">
    <div class="panel-heading wheel-heading">
      <div><p class="eyebrow">NATAL WHEEL</p><h2>ネイタルチャート</h2><p>ASCを左に配置したホロスコープ星図</p></div>
      <button class="aspect-toggle" type="button" :aria-pressed="showAspects" @click="showAspects = !showAspects">
        <span :class="{ active: showAspects }" />アスペクト
      </button>
    </div>

    <div class="wheel-stage">
      <svg viewBox="0 0 720 720" role="img" aria-labelledby="natal-wheel-title natal-wheel-description">
        <title id="natal-wheel-title">ネイタルチャートのホロスコープ星図</title>
        <desc id="natal-wheel-description">12サイン、12ハウス、主要天体とアスペクトを円形に配置した図</desc>
        <defs>
          <radialGradient id="wheel-background" cx="50%" cy="46%" r="55%">
            <stop offset="0" stop-color="#14203a" stop-opacity=".95" />
            <stop offset="1" stop-color="#080f22" stop-opacity=".98" />
          </radialGradient>
          <filter id="planet-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        <circle :cx="center" :cy="center" :r="outerRadius" class="wheel-base" />
        <circle :cx="center" :cy="center" :r="zodiacInnerRadius" class="zodiac-inner" />
        <circle :cx="center" :cy="center" :r="aspectRadius" class="aspect-boundary" />

        <g class="degree-ticks" aria-hidden="true">
          <line v-for="tick in ticks" :key="tick.longitude"
            :x1="pointAt(tick.longitude, outerRadius).x" :y1="pointAt(tick.longitude, outerRadius).y"
            :x2="pointAt(tick.longitude, tick.major ? outerRadius - 12 : outerRadius - 6).x"
            :y2="pointAt(tick.longitude, tick.major ? outerRadius - 12 : outerRadius - 6).y"
            :class="{ major: tick.major }" />
        </g>

        <g class="zodiac-ring">
          <g v-for="(item, index) in signs" :key="item.key">
            <line :x1="pointAt(index * 30, zodiacInnerRadius).x" :y1="pointAt(index * 30, zodiacInnerRadius).y"
              :x2="pointAt(index * 30, outerRadius).x" :y2="pointAt(index * 30, outerRadius).y" />
            <text :x="pointAt(index * 30 + 15, 296).x" :y="pointAt(index * 30 + 15, 296).y" class="sign-glyph">{{ item.glyph }}<title>{{ item.label }}</title></text>
          </g>
        </g>

        <g class="house-lines">
          <line v-for="line in houseLines" :key="line.number"
            :x1="line.inner.x" :y1="line.inner.y" :x2="line.outer.x" :y2="line.outer.y"
            :class="{ angular: line.angular }" />
          <text v-for="label in houseLabels" :key="label.number" :x="label.position.x" :y="label.position.y">{{ label.number }}</text>
        </g>

        <g v-if="showAspects" class="aspect-lines">
          <line v-for="(aspect, index) in aspects" :key="`${aspect.p1_name}-${aspect.p2_name}-${index}`"
            :x1="aspect.from.x" :y1="aspect.from.y" :x2="aspect.to.x" :y2="aspect.to.y"
            :stroke="aspect.style.color" :stroke-dasharray="aspect.style.dash" :opacity="aspect.opacity">
            <title>{{ names[aspect.p1_name] }} − {{ names[aspect.p2_name] }} / {{ aspect.aspect }} / オーブ {{ formatDegreeMinutes(aspect.orbit) }}</title>
          </line>
        </g>

        <g class="planet-points">
          <g v-for="point in planetPositions" :key="point.name">
            <line :x1="point.anchor.x" :y1="point.anchor.y" :x2="point.connector.x" :y2="point.connector.y" :stroke="point.color" />
            <circle :cx="point.anchor.x" :cy="point.anchor.y" r="4" :fill="point.color" filter="url(#planet-glow)" />
            <text :x="point.labelPosition.x" :y="point.labelPosition.y - 2" :fill="point.color" class="planet-glyph" :class="{ axis: point.name === 'Ascendant' || point.name === 'Medium_Coeli' }">{{ point.glyph }}</text>
            <text :x="point.labelPosition.x" :y="point.labelPosition.y + 12" class="planet-degree">{{ formatDegreeMinutes(point.position) }}{{ point.retrograde ? ' ℞' : '' }}</text>
            <title>{{ point.label }} {{ point.sign }} {{ formatDegreeMinutes(point.position) }}</title>
          </g>
        </g>

        <circle :cx="center" :cy="center" r="5" class="chart-center" />
        <text :x="center" :y="center - 12" class="center-mark">✦</text>
      </svg>
    </div>

    <div class="wheel-legend" aria-label="アスペクト凡例">
      <span><i class="conjunction" />合</span><span><i class="harmonious" />トライン・セクスタイル</span><span><i class="challenging" />オポジション・スクエア</span>
    </div>
  </section>
</template>

<style scoped>
.natal-wheel-panel { margin-bottom: 24px; overflow: hidden; }
.wheel-heading > div > p:last-child { margin: 7px 0 0; color: var(--muted); font-size: 12px; }
.aspect-toggle { display: inline-flex; align-items: center; gap: 9px; padding: 8px 11px; border: 1px solid var(--line); border-radius: 20px; background: rgba(255,255,255,.025); color: #9aa8bc; font-size: 11px; cursor: pointer; }
.aspect-toggle > span { width: 25px; height: 14px; padding: 2px; border-radius: 20px; background: #344059; transition: .2s ease; }
.aspect-toggle > span::after { content: ''; display: block; width: 10px; height: 10px; border-radius: 50%; background: #8793a7; transition: .2s ease; }
.aspect-toggle > span.active { background: rgba(215,180,93,.38); }
.aspect-toggle > span.active::after { transform: translateX(11px); background: var(--gold-bright); }
.wheel-stage { width: min(100%, 790px); margin: 0 auto; padding: 22px 28px 10px; }
svg { display: block; width: 100%; height: auto; overflow: visible; font-family: 'Noto Sans JP', sans-serif; }
.wheel-base { fill: url(#wheel-background); stroke: rgba(215,180,93,.42); stroke-width: 2; }
.zodiac-inner { fill: none; stroke: rgba(215,180,93,.28); stroke-width: 1.4; }
.aspect-boundary { fill: rgba(5,11,25,.23); stroke: rgba(174,190,216,.13); }
.degree-ticks line { stroke: rgba(215,180,93,.27); stroke-width: .8; }
.degree-ticks line.major { stroke: rgba(215,180,93,.64); stroke-width: 1.5; }
.zodiac-ring line { stroke: rgba(215,180,93,.28); }
.sign-glyph { fill: #d7b45d; font-family: Georgia, 'Times New Roman', serif; font-size: 25px; text-anchor: middle; dominant-baseline: central; }
.house-lines line { stroke: rgba(150,169,201,.17); stroke-width: 1; }
.house-lines line.angular { stroke: rgba(215,180,93,.42); stroke-width: 1.6; }
.house-lines text { fill: #66758d; font: 500 10px 'Noto Sans JP', sans-serif; text-anchor: middle; dominant-baseline: central; }
.aspect-lines line { stroke-width: 1.3; vector-effect: non-scaling-stroke; }
.planet-points line { stroke-width: .85; opacity: .62; }
.planet-glyph { font-family: Georgia, 'Times New Roman', serif; font-size: 22px; text-anchor: middle; dominant-baseline: central; filter: drop-shadow(0 1px 4px rgba(0,0,0,.8)); }
.planet-glyph.axis { font: 700 12px 'Noto Sans JP', sans-serif; }
.planet-degree { fill: #7f8da1; font: 500 8px 'Noto Sans JP', sans-serif; text-anchor: middle; }
.chart-center { fill: #d7b45d; opacity: .38; }
.center-mark { fill: rgba(215,180,93,.25); font-size: 18px; text-anchor: middle; }
.wheel-legend { display: flex; justify-content: center; flex-wrap: wrap; gap: 12px 24px; padding: 0 24px 23px; color: #7d8ba0; font-size: 10px; }
.wheel-legend span { display: inline-flex; align-items: center; gap: 7px; }
.wheel-legend i { width: 25px; height: 1px; background: #d7b45d; }
.wheel-legend i.harmonious { background: #72a9d8; }
.wheel-legend i.challenging { background: #d97979; }
@media (max-width: 680px) {
  .wheel-heading { align-items: flex-start; }
  .wheel-heading > div > p:last-child { font-size: 11px; }
  .aspect-toggle { padding: 7px 9px; font-size: 10px; }
  .wheel-stage { padding: 14px 8px 6px; }
  .planet-degree { display: none; }
  .wheel-legend { gap: 9px 15px; padding-bottom: 18px; font-size: 9px; }
}
</style>

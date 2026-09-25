<script setup lang="ts">
import type { ClientOverview } from '~/types/client'

defineProps<{ client: ClientOverview; compact?: boolean }>()

const signLabel: Record<string, string> = {
  Ari: '牡羊座', Tau: '牡牛座', Gem: '双子座', Can: '蟹座', Leo: '獅子座', Vir: '乙女座',
  Lib: '天秤座', Sco: '蠍座', Sag: '射手座', Cap: '山羊座', Aqu: '水瓶座', Pis: '魚座',
  Aries: '牡羊座', Taurus: '牡牛座', Gemini: '双子座', Cancer: '蟹座', Virgo: '乙女座',
  Libra: '天秤座', Scorpio: '蠍座', Sagittarius: '射手座', Capricorn: '山羊座', Aquarius: '水瓶座', Pisces: '魚座',
}
const label = (sign: string | null) => sign ? signLabel[sign] || sign : '未計算'
const date = (value: string) => new Intl.DateTimeFormat('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' }).format(new Date(`${value}T00:00:00`))
</script>

<template>
  <NuxtLink :to="`/clients/${client.id}`" class="client-row" :class="{ compact }" :aria-label="`${client.name}さんの詳細を開く`">
    <div class="avatar">{{ client.name.slice(0, 1) }}</div>
    <div class="client-identity">
      <h3>{{ client.name }}</h3>
      <p><AppIcon name="calendar" />{{ date(client.birth_date) }}<span>·</span><AppIcon name="pin" />{{ client.birth_place }}</p>
    </div>
    <div v-if="client.has_chart" class="signatures" aria-label="主要3天体">
      <span><small>☉ 太陽</small>{{ label(client.sun_sign) }}</span>
      <span><small>☽ 月</small>{{ label(client.moon_sign) }}</span>
      <span><small>ASC</small>{{ label(client.ascendant_sign) }}</span>
    </div>
    <span v-else class="status-badge">チャート未作成</span>
    <span class="row-arrow" aria-hidden="true"><AppIcon name="arrow" /></span>
  </NuxtLink>
</template>

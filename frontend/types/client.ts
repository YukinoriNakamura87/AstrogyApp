export type ClientOverview = {
  id: number
  name: string
  birth_date: string
  birth_time: string | null
  birth_place: string
  updated_at: string | null
  has_chart: boolean
  sun_sign: string | null
  moon_sign: string | null
  ascendant_sign: string | null
}

export type ClientListResponse = { items: ClientOverview[]; total: number }

export type DashboardResponse = {
  client_count: number
  chart_count: number
  session_count: number
  recent_clients: ClientOverview[]
  recent_sessions: Array<{ id: number; client_name: string; held_at: string; title: string }>
}

export type ClientDetail = {
  id: number
  name: string
  birth_date: string
  birth_time: string | null
  birth_place: string
  birth_latitude: string
  birth_longitude: string
  birth_timezone: string
  created_at: string | null
  updated_at: string | null
}

export type NatalChart = {
  client_id: number
  calculation_version: string
  calculation: {
    subject: Record<string, unknown>
    aspects: Array<Record<string, unknown>>
    element_distribution?: Record<string, number>
    quality_distribution?: Record<string, number>
    [key: string]: unknown
  }
}

export type ClientProfileResponse = {
  client: ClientDetail
  chart: NatalChart | null
}

export type ChartInterpretationMemo = {
  id: number
  planet: string
  content: string
  created_at: string | null
  updated_at: string | null
}

export type ChartMemosResponse = { items: ChartInterpretationMemo[] }

export type LillyScoreItem = {
  code: string
  label: string
  points: number
  description: string
  status: 'awarded' | 'neutral' | 'unavailable'
  related_body: string | null
}

export type LillyScoreSection = { total: number; items: LillyScoreItem[] }

export type LillyPlanetScore = {
  planet: string
  essential: LillyScoreSection
  accidental: LillyScoreSection
  total: number
}

export type LillyScoreResponse = {
  sect: 'day' | 'night'
  planets: LillyPlanetScore[]
  essential_total: number
  accidental_total: number
  grand_total: number
  warnings: string[]
}

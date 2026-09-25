export function formatDegreeMinutes(value: number): string {
  if (!Number.isFinite(value)) return '—'
  const totalMinutes = Math.floor(Math.abs(value) * 60 + 1e-9)
  const prefix = value < 0 ? '-' : ''
  return `${prefix}${Math.floor(totalMinutes / 60)}°${String(totalMinutes % 60).padStart(2, '0')}′`
}

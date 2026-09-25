type ValidationIssue = { loc?: unknown[]; msg?: string }

export function readableApiError(error: any, fallback = '通信に失敗しました。'): string {
  const detail = error?.data?.data?.detail ?? error?.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item: ValidationIssue) => {
        const location = Array.isArray(item?.loc) ? item.loc.join('.') : ''
        return [location, item?.msg].filter(Boolean).join(': ')
      })
      .filter(Boolean)
    if (messages.length) return messages.join(' / ')
  }
  return typeof error?.message === 'string' && error.message.trim()
    ? error.message
    : fallback
}

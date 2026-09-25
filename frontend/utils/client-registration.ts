export type ApiFetch = (
  request: string,
  options?: Record<string, unknown>,
) => Promise<unknown>

export type RegistrationResult = {
  clientId: number
  chartCalculationFailed: boolean
}

export async function registerClientAndPrepareChart(
  apiFetch: ApiFetch,
  payload: Record<string, unknown>,
): Promise<RegistrationResult> {
  const client = await apiFetch('/api/clients', {
    method: 'POST',
    body: payload,
  }) as { id?: unknown }

  if (!Number.isInteger(client.id) || Number(client.id) <= 0) {
    throw new Error('登録結果からクライアントIDを取得できませんでした。')
  }

  const clientId = Number(client.id)
  let chartCalculationFailed = false
  try {
    await apiFetch(`/api/clients/${clientId}/chart`)
  } catch {
    // Registration has already succeeded. The detail page provides a safe retry.
    chartCalculationFailed = true
  }

  return { clientId, chartCalculationFailed }
}

export function clientDetailLocation(result: RegistrationResult) {
  return {
    path: `/clients/${result.clientId}`,
    query: result.chartCalculationFailed ? { chart: 'failed' } : {},
  }
}

import { describe, expect, it, vi } from 'vitest'

import {
  clientDetailLocation,
  registerClientAndPrepareChart,
} from '../utils/client-registration'

describe('client registration flow', () => {
  it('registers, calculates the chart, and returns the detail destination', async () => {
    const apiFetch = vi.fn()
      .mockResolvedValueOnce({ id: 12 })
      .mockResolvedValueOnce({ client_id: 12 })

    const result = await registerClientAndPrepareChart(apiFetch, { name: 'Yuki' })

    expect(apiFetch).toHaveBeenNthCalledWith(1, '/api/clients', {
      method: 'POST', body: { name: 'Yuki' },
    })
    expect(apiFetch).toHaveBeenNthCalledWith(2, '/api/clients/12/chart')
    expect(clientDetailLocation(result)).toEqual({ path: '/clients/12', query: {} })
  })

  it('keeps the registered client and sends chart failures to the retry screen', async () => {
    const apiFetch = vi.fn()
      .mockResolvedValueOnce({ id: 13 })
      .mockRejectedValueOnce(new Error('chart failed'))

    const result = await registerClientAndPrepareChart(apiFetch, { name: 'Emi' })

    expect(result).toEqual({ clientId: 13, chartCalculationFailed: true })
    expect(clientDetailLocation(result)).toEqual({
      path: '/clients/13', query: { chart: 'failed' },
    })
  })

  it('does not calculate a chart when registration fails', async () => {
    const apiFetch = vi.fn().mockRejectedValue(new Error('registration failed'))

    await expect(registerClientAndPrepareChart(apiFetch, {})).rejects.toThrow('registration failed')
    expect(apiFetch).toHaveBeenCalledTimes(1)
  })

  it('rejects an invalid registration response before chart calculation', async () => {
    const apiFetch = vi.fn().mockResolvedValue({})

    await expect(registerClientAndPrepareChart(apiFetch, {})).rejects.toThrow('クライアントID')
    expect(apiFetch).toHaveBeenCalledTimes(1)
  })
})

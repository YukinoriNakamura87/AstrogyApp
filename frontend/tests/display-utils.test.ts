import { describe, expect, it } from 'vitest'

import { formatDegreeMinutes } from '../utils/angle'
import { readableApiError } from '../utils/api-error'

describe('display utilities', () => {
  it('formats angles consistently as degrees and whole minutes', () => {
    expect(formatDegreeMinutes(0.847024)).toBe('0°50′')
    expect(formatDegreeMinutes(29.90118)).toBe('29°54′')
    expect(formatDegreeMinutes(Number.NaN)).toBe('—')
  })

  it('reads backend detail and validation errors', () => {
    expect(readableApiError({ data: { data: { detail: '保存できません' } } })).toBe('保存できません')
    expect(readableApiError({ data: { detail: [{ loc: ['body', 'name'], msg: 'required' }] } })).toBe('body.name: required')
  })
})

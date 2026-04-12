// frontend/src/lib/beamHash.ts
import type { BeamInput } from '@/types/api'

/**
 * Encodes a BeamInput to a base64 string suitable for use in URL hash.
 * Produces the raw base64 — caller adds '#' prefix when setting location.hash.
 */
export function encodeBeamHash(input: BeamInput): string {
  return btoa(encodeURIComponent(JSON.stringify(input)))
}

/**
 * Decodes a base64 hash string to BeamInput.
 * Returns null on any error (malformed base64, invalid JSON, missing fields).
 */
export function decodeBeamHash(hash: string): BeamInput | null {
  if (!hash) return null
  try {
    const json = decodeURIComponent(atob(hash))
    const parsed = JSON.parse(json)
    // Basic shape validation — must have length and supports array
    if (
      typeof parsed.length !== 'number' ||
      !Array.isArray(parsed.supports)
    ) return null
    return parsed as BeamInput
  } catch {
    return null
  }
}

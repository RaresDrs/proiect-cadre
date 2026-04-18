import type { FrameInput } from '@/types/api'

/**
 * Encodes a FrameInput to a base64 string for use in URL hash.
 * Caller adds '#' prefix when setting location.hash.
 */
export function encodeFrameHash(input: FrameInput): string {
  return btoa(encodeURIComponent(JSON.stringify(input)))
}

/**
 * Decodes a base64 hash string to FrameInput.
 * Returns null on any error: empty string, malformed base64, invalid JSON,
 * or missing required fields (nodes array, bars array).
 */
export function decodeFrameHash(hash: string): FrameInput | null {
  if (!hash) return null
  try {
    const json = decodeURIComponent(atob(hash))
    const parsed = JSON.parse(json)
    // Basic shape validation — must have nodes and bars arrays
    if (!Array.isArray(parsed.nodes) || !Array.isArray(parsed.bars)) return null
    return parsed as FrameInput
  } catch {
    return null
  }
}

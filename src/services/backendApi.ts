export type PlannerInput = {
  natural_language: string
  preferences: {
    duration_minutes: number
    pace: 'slow'|'balanced'|'challenge'
    avoid_climbing: boolean
    avoid_sun: boolean
    with_child: boolean
    preferred_animals: string[]
    must_visit: string[]
  }
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8765'

export function getUserId() {
  let userId = localStorage.getItem('hs-user-id')
  if (!userId) {
    userId = globalThis.crypto?.randomUUID?.() || `visitor-${Date.now()}-${Math.random().toString(36).slice(2)}`
    localStorage.setItem('hs-user-id', userId)
  }
  return userId
}

export async function saveCompanionSelection(companion:string, source:'quiz'|'blind_box'|'manual'='manual') {
  const response = await fetch(`${API_BASE}/api/profile/companion`, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id:getUserId(), companion, source}) })
  if (!response.ok) throw new Error(`save companion failed: ${response.status}`)
  return response.json() as Promise<{user_id:string; companion:string; source:string; updated_at:string}>
}

export async function getCompanionSelection() {
  const response = await fetch(`${API_BASE}/api/profile/${encodeURIComponent(getUserId())}/companion`)
  if (response.status === 404) return null
  if (!response.ok) throw new Error(`get companion failed: ${response.status}`)
  return response.json() as Promise<{user_id:string; companion:string; source:string; updated_at:string}>
}

export async function planRoute(input: PlannerInput) {
  const response = await fetch(`${API_BASE}/api/route/plan`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(input) })
  if (!response.ok) throw new Error(`route plan failed: ${response.status}`)
  const result = await response.json()
  localStorage.setItem('hs-last-route', JSON.stringify(result))
  return result
}

export async function getParkStatus() {
  const response = await fetch(`${API_BASE}/api/park/status`)
  if (!response.ok) throw new Error(`park status failed: ${response.status}`)
  return response.json()
}

export async function askCompanion(input: { question:string; context?:string; companion?:string; language?:string }) {
  const response = await fetch(`${API_BASE}/api/assistant/ask`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(input) })
  if (!response.ok) throw new Error(`assistant failed: ${response.status}`)
  return response.json() as Promise<{answer:string; source:string}>
}

export async function synthesizeSpeech(text:string, voice?:string, language='zh-CN') {
  const response = await fetch(`${API_BASE}/api/voice/synthesize`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text, voice, language}) })
  if (!response.ok) throw new Error(`tts failed: ${response.status}`)
  return response.json() as Promise<{enabled:boolean; mime_type?:string; audio_base64?:string; message?:string}>
}

export async function transcribeSpeech(audioUrl:string, language='zh-CN', model?:string) {
  const response = await fetch(`${API_BASE}/api/voice/transcribe`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({audio_url:audioUrl, language, model}) })
  if (!response.ok) throw new Error(`asr failed: ${response.status}`)
  return response.json() as Promise<{enabled:boolean; text:string; language:string; model?:string; message?:string}>
}

export async function generateStory(input:{companion:string; current_poi:string; clue?:string; route?:unknown[]; collected_clues?:string[]; completed_npcs?:string[]; style?:string; persona?:Record<string,unknown>}) {
  const response = await fetch(`${API_BASE}/api/story/generate`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(input) })
  if (!response.ok) throw new Error(`story failed: ${response.status}`)
  return response.json() as Promise<{story:Record<string,unknown>; source:string}>
}

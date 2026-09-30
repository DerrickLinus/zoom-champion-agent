import { points } from '../data'

// Demo-only service boundary. Replace these pure functions with API calls later.
export const profileService = { createCompanion: () => ({ name: '团团', type: '考拉式慢游伴', level: 2 }) }
export const routeService = {
  generate: (preferences: Record<string, string>) => ({ name: '轻松亲子线', duration: preferences.time || '2小时', points }),
  alternatives: () => ['轻松亲子线', '动物活跃优先线', '故事探索线'],
  insertRestStop: (route: typeof points) => route.length > 3 ? [route[0], route[1], points[3], route[2], ...route.slice(4)] : route,
  undo: (route: typeof points) => route,
}
export const realtimeService = {
  getSnapshot: () => ({ updatedAt: '14:32', crowd: '低', weather: '晴 · 29°', animalActivity: '中等' }),
}
export const contentService = { getStory: () => ({ title: '寻找森林里消失的歌声', version: '亲子故事版' }) }
export const growthService = { add: (current: number, value: number) => current + value }

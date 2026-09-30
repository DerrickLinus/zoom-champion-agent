import { knowledgeBase, KnowledgeChunk } from '../data/knowledgeBase'

const terms = (text:string) => text.toLowerCase().split(/[，。！？；、\s?]+/).filter(x=>x.length>1)

export const retrieve = (query:string, limit=3, language:KnowledgeChunk['language']='zh-CN', poiId?:string): KnowledgeChunk[] => {
  const q = terms(query)
  return knowledgeBase.map(chunk => ({ chunk, score:q.reduce((sum,word)=>sum + ((chunk.text+chunk.title+chunk.tags.join('')).toLowerCase().includes(word)?1:0),0) + (chunk.language===language?1:0) + (poiId&&chunk.poiId===poiId?2:0) })).sort((a,b)=>b.score-a.score).filter(x=>x.score>0).slice(0,limit).map(x=>x.chunk)
}

export const answerFromKnowledge = (query:string) => {
  const hits = retrieve(query)
  if (!hits.length) return { answer:'我暂时没有在红山官方素材里找到对应内容。你可以换个问法，比如“貉什么时候更活跃？”或“怎么做到不打扰地观察？”。', sources:[] as KnowledgeChunk[] }
  const lead = hits[0]
  return { answer:`根据红山资料：${lead.text} 你也可以继续问我关于场馆、动物行为和文明观察的问题。`, sources:hits }
}

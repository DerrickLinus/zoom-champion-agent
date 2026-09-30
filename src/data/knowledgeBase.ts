export type KnowledgeChunk = { id:string; title:string; source:string; sourceSection?:string; poiId?:string; language?:'zh-CN'|'en'; contentType?:'fact'|'welfare'|'brand'|'story_style'; reviewed?:boolean; tags:string[]; text:string }

export const knowledgeBase: KnowledgeChunk[] = [
  { id:'welfare', title:'一切为了动物', source:'宣传册中文版.pdf', tags:['动物福利','参观'], text:'红山森林动物园以一切为了动物为核心方针。最好的观赏不是打扰，而是理解、尊重和等待。' },
  { id:'raccoon-dog', title:'貉：城市适应高手', source:'讲解稿.docx', tags:['貉','本土物种','行为'], text:'貉通常在清晨和黄昏更活跃。观察貉时不必追逐或敲击玻璃，给它们保留自己的距离。' },
  { id:'observation', title:'不打扰地观察', source:'宣传册中文版.pdf', tags:['文明参观','观察','动物福利'], text:'请不要敲击玻璃、投喂、追逐或使用强闪光；动物休息时请耐心等待。安静下来，先听见再看见，是更好的观赏方式。' },
  { id:'pond', title:'一个池塘的自循环', source:'讲解稿.docx', tags:['湿地','生态循环'], text:'池塘里有鱼、虾、螺和水生植物。植物、虾、螺和鱼互相依赖，形成不需要人工投喂也能维持的生态平衡。' },
  { id:'panda', title:'大熊猫的生活空间', source:'讲解稿.docx', tags:['大熊猫','场馆','动物福利'], text:'熊猫馆根据大熊猫不惧寒湿、最怕炎热的习性设计，活动区域会根据季节和天气使用。' },
  { id:'native', title:'本土物种保育区', source:'讲解稿.docx', tags:['本土物种','保育','生态'], text:'本土物种保育区还原长江中下游的农田、湿地、山林生态系统，承担野生动物收容救助和保育功能。' },
]

import { animals, nodeMissions, points } from '../data'

export type StoryMode = 'detective' | 'rescue' | 'archive' | 'treasure' | 'growth' | 'comedy' | 'forest' | 'letter'

export type GeneratedStory = {
  title:string
  subtitle:string
  hook:string
  chapters:{point:string; label:string; text:string; action:string}[]
  ending:string
  modeLabel:string
}

export const storyModeOptions:{mode:StoryMode;label:string;sub:string;icon:string}[] = [
  {mode:'detective', label:'森林侦探', sub:'找出隐藏线索', icon:'⌕'},
  {mode:'rescue', label:'动物救援', sub:'寻找失联伙伴', icon:'♡'},
  {mode:'archive', label:'时空档案', sub:'拼回园区记忆', icon:'▣'},
  {mode:'treasure', label:'森林宝藏', sub:'集齐失落印记', icon:'✦'},
  {mode:'growth', label:'搭子成长', sub:'解锁专属结局', icon:'❋'},
  {mode:'comedy', label:'轻喜剧闯关', sub:'帮搭子收拾残局', icon:'☻'},
]

const modeLabels:Record<StoryMode,string> = {
  detective:'森林侦探案',
  rescue:'动物救援任务',
  archive:'时空档案馆',
  treasure:'森林宝藏计划',
  growth:'动物搭子成长冒险',
  comedy:'森林轻喜剧闯关',
  forest:'森林秘境任务',
  letter:'动物来信',
}

const cases:Record<StoryMode,{title:string;object:string;reveal:string}> = {
  detective:{title:'失落的第四枚印记',object:'一张只留下三个动物脚印的旧路线图',reveal:'线索并没有指向一个坏人，而是提醒你重新看见那些容易被忽略的生命。'},
  rescue:{title:'请把小满带回森林边缘',object:'一位动物伙伴留下的食物、声音和脚印',reveal:'真正的救援不是把动物带到人群面前，而是帮它找到安全、熟悉、可以按自己节奏生活的地方。'},
  archive:{title:'一张没有终点的老地图',object:'一张被折过很多次、缺少最后一页的园区旧地图',reveal:'你拼回的不是一张路线图，而是几代人和动物共同留下的园区记忆。'},
  treasure:{title:'失落的森林印记',object:'一枚被拆成五部分的神秘印记',reveal:'宝藏不是被藏起来的奖品，而是每个节点都愿意为森林留下的一点善意。'},
  growth:{title:'搭子今天学会了什么',object:'动物搭子写给你的五个小问题',reveal:'最后被改变的不是动物，而是你们之间越来越默契的相处方式。'},
  comedy:{title:'搭子闯下的小麻烦',object:'一只被咬出缺口的任务竹筒和一串错位的印章',reveal:'森林没有要求你成为完美的侦探，只希望你愿意和搭子一起把事情做完。'},
  forest:{title:'湿地里的回声',object:'一段需要在安静观察中才能听见的自然回应',reveal:'森林的答案不一定要被带走，有时它只需要被认真听见。'},
  letter:{title:'搭子写给你的信',object:'一封没有署名、只留下脚印和树叶的信',reveal:'你和搭子交换了一个愿望：以后每次来红山，都记得给彼此留一点自由。'},
}

function animalClue(animal:typeof animals[number]){
  if(animal.species.includes('貉')) return `${animal.name}把线索藏进落叶里，等一个愿意慢慢找的人。`
  if(animal.species.includes('赤狐')) return `${animal.name}没有靠近，只留下一条保持距离的路线。它想确认你是否懂得尊重边界。`
  if(animal.species.includes('獐')) return `${animal.name}把你带到水边：这里的答案不在某一个动物身上，而在整个生境的关系里。`
  return `${animal.name}没有催你寻找答案。它知道，先观察动物如何选择，故事才会真正开始。`
}

export function generateStory(animal:typeof animals[number], routeMode:string, mode:StoryMode, seed=Math.floor(Math.random()*3)):GeneratedStory{
  const mystery=cases[mode]
  const names=points.slice(0,5).map(x=>x.name)
  const missions=nodeMissions.slice(0,5)
  const chapters=names.map((point,i)=>{
    const mission=missions[i]
    const previous=i===0?'入口处，搭子把第一件奇怪的东西交到你手里。':`上一站留下的线索，指向了${point}。`
    const textByMode:Record<StoryMode,string>={
      detective:`${previous}今天要查的不是一件惊天大案，而是${mystery.object}。${animal.name}提醒你：先记录现场，再听听 NPC 的证词。${i===1?'你发现，第一份证词和地图上的方向并不一致。':i===3?'几条线索在这里交汇，真正可疑的不是消失，而是有人一直没有被看见。':'每个细节都可能改变你对这条路线的判断。'}`,
      rescue:`${previous}${animal.name}发现伙伴可能暂时离开了熟悉的活动范围。你要沿路线收集${i===0?'声音':i===1?'食物痕迹':i===2?'脚印':i===3?'栖息地线索':'最后一段安全信号'}，但不能追赶或惊扰它。`,
      archive:`${previous}旧地图在${point}留下了一段缺页记忆。${i===0?'先找到地图上的旧标记。':i===1?'NPC讲起了这里曾经发生的一件小事。':i===2?'你把现在看到的景象和过去的记录叠在一起。':'最后一页的内容，藏在你亲自走过的路线里。'}`,
      treasure:`${previous}这里藏着一枚森林印记。完成 NPC 的小任务，你会得到一块新的图案；把它和前面的印记拼在一起，才能知道宝藏下一站在哪里。`,
      growth:`${previous}${animal.name}提出了一个问题：你会选择靠近、等待，还是换一条更安静的路？你的选择会被记进搭子的成长册，影响它最后怎样称呼你。`,
      comedy:`${previous}糟糕，${animal.name}又把${i===0?'任务卡':i===1?'一枚印章':i===2?'线索竹筒':i===3?'地图角落':'最后的奖励提示'}弄丢了。你需要完成 NPC 的任务，帮它把这场小混乱收拾好。`,
      forest:`${previous}${animal.name}把你带到一处适合安静观察的地方。这里的线索不是物品，而是风、树影和动物留下的生活痕迹。`,
      letter:`${previous}${animal.name}在这里给你写下信里的下一句话：${animalClue(animal)}你需要用一次温柔的观察，回信给它。`,
    }
    const actionByMode:Record<StoryMode,string>={
      detective:'记录一个现场细节，再向 NPC 说出你的推理',
      rescue:'寻找线索但保持距离，不追逐、不投喂、不敲玻璃',
      archive:'在节点收集一段记忆，并把它放回旧地图对应的位置',
      treasure:'完成 NPC 互动，领取这一站的森林印记',
      growth:'做出一个你的选择，让搭子记住今天的相处方式',
      comedy:'帮搭子完成补救任务，把错位的线索重新排好',
      forest:'安静观察一会儿，记录一条不打扰动物的发现',
      letter:'替搭子完成一次观察，并把你的回应写进故事里',
    }
    const labels:Record<StoryMode,string[]>={
      detective:['委托受理','第一份证词','NPC 证词','关键转折','案件结案'],
      rescue:['发现失联','寻找声音','追踪脚印','确认生境','安全回信'],
      archive:['获得旧图','翻开档案','对照记忆','补上缺页','档案归还'],
      treasure:['领取空印','第一枚印记','NPC 试炼','藏宝图成形','开启宝藏'],
      growth:['认识搭子','它开始信任你','交换一个选择','形成默契','写下结局'],
      comedy:['麻烦出现','先找回印章','竹筒去哪了','临时补救','终于收拾好'],
      forest:['进入林间','落叶回应','水边关系','风的方向','森林回信'],
      letter:['第一封信','信里的脚印','NPC 回信','搭子沉默时','写给来访者'],
    }
    return {point,label:labels[mode][i],text:textByMode[mode],action:actionByMode[mode]}
  })
  return {
    title:mystery.title,
    subtitle:`${animal.name} × ${routeMode} · ${modeLabels[mode]}`,
    hook:`今天不是简单打卡，而是和${animal.name}一起完成任务：${mystery.object}为什么会出现在你的路线里？`,
    chapters,
    ending:`${animal.name}陪你走完了这条路线。${mystery.reveal}`,
    modeLabel:modeLabels[mode],
  }
}

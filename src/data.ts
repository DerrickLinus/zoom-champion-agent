export type Page = 'welcome'|'quiz'|'match'|'home'|'plan'|'route'|'story'|'tour'|'venue'|'complete'|'growth'|'ask'
export const points = [
  { id:'gate', name:'园区入口', sub:'从一阵树叶的沙沙声开始', x:16, y:74, icon:'⌂' },
  { id:'noah', name:'诺亚方舟区', sub:'听见水边的风', x:31, y:56, icon:'◇' },
  { id:'panda', name:'金陵大熊猫苑', sub:'今天很想见面的朋友', x:43, y:36, icon:'●' },
  { id:'spirit', name:'亚洲灵长馆', sub:'团团最期待的见面', x:57, y:42, icon:'◒' },
  { id:'rest', name:'林间休息区', sub:'坐下来，分享一口风', x:47, y:69, icon:'⌁' },
  { id:'native', name:'本土动物区', sub:'把脚步交给森林', x:72, y:59, icon:'♧' },
  { id:'exit', name:'推荐离园出口', sub:'带着故事回到城市', x:85, y:76, icon:'↗' },
]
export const animals = [
  { name:'狐獴', type:'嘿！你来啦，我已经坐不住啦！', emoji:'狐獴', color:'#d6a15f', species:'狐獴', tags:['反应快','重点明确','轻快机灵'], quote:'先抓住重点，再一起看看还有什么新发现。', active:'精神十足', story:'迅速出现的关键线索' },
  { name:'白脸僧面猴', type:'你好，很高兴认识你，请多指教。', emoji:'白脸僧面猴', color:'#879487', species:'白脸僧面猴', tags:['知识严谨','解释完整','平静克制'], quote:'把现象和原因讲清楚，观察才真正有意义。', active:'安静观察', story:'现象背后的完整答案' },
  { name:'考拉', type:'嗨～我刚睡醒，你来得正好。', emoji:'考拉', color:'#9ca5a0', species:'考拉', tags:['表达简洁','直接可靠','情绪稳定'], quote:'一句话说清重点，然后慢慢看。', active:'安静休息', story:'最短的一条重要提示' },
  { name:'水獭', type:'哇！是你呀，今天一起玩个痛快！', emoji:'水獭', color:'#8aa99d', species:'水獭', tags:['热情有戏','故事丰富','情绪生动'], quote:'准备好了吗？这条线索背后可有一段好故事。', active:'活跃玩耍', story:'水边突然发生的小故事' },
  { name:'小熊猫', type:'你好呀，见到你，今天心情都变好啦。', emoji:'小熊猫', color:'#d98858', species:'小熊猫', tags:['温柔耐心','节奏均衡','细腻照顾'], quote:'不用着急，我会陪你按最舒服的节奏慢慢听。', active:'林间散步', story:'一片落叶的温柔来信' },
]
export const chapters = ['在入口收到一封来自森林的信','跟着团伙伴的脚印走进本土物种保育区','在林间休息区整理线索','找到属于你的那一段动物故事']
export const nodeMissions = [
  { clue:'一片有三道缺口的叶子', npc:'林间邮差', task:'脑筋急转弯', prompt:'什么东西只有在你停下来时，才会越来越清楚？', answer:'森林的声音', story:'邮差说，这片叶子来自一封没有署名的信。' },
  { clue:'一枚被落叶包住的种子', npc:'落叶侦探', task:'线索问答', prompt:'貉为什么喜欢落叶和断木？', answer:'更接近它的自然生活环境', story:'落叶侦探把线索藏在貉喜欢的荒丘野地里。' },
  { clue:'一张池塘生态关系卡', npc:'湿地观察员', task:'找出生态伙伴', prompt:'鱼的排泄物最后会成为谁的养分？', answer:'水生植物', story:'池塘里的每个生命都在为别的生命留下线索。' },
  { clue:'一根没有被带走的红色羽毛', npc:'边界守护者', task:'猜拳挑战', prompt:'面对正在休息的动物，最好的动作是什么？', answer:'保持距离，安静等待', story:'NPC把羽毛放回树下：真正的礼物，是不把它带走。' },
  { clue:'一张盖满树影的回信', npc:'森林回声员', task:'文化知识问答', prompt:'红山动物园最核心的价值观是什么？', answer:'一切为了动物', story:'最后一枚线索提醒你，游客是来访的客人，动物才是这里的主人。' },
]
export const rewards = [
  { id:'leaf-card', name:'森林线索卡', cost:60, desc:'完成 3 个 NPC 任务即可兑换', status:'可兑换' },
  { id:'stamp-book', name:'红山故事印记册', cost:120, desc:'集齐 5 枚节点印章', status:'即将解锁' },
  { id:'badge', name:'不打扰观察者徽章', cost:180, desc:'完成一次完整故事线并遵守观察公约', status:'未来兑换' },
]

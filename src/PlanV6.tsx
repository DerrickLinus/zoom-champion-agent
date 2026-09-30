import { useMemo, useState } from 'react'
import { ArrowRight, Check, Mic, Plus, Sparkles, X } from 'lucide-react'
import { planRoute } from './services/backendApi'
import './plan-v6.css'

type Props = { s:any; setS:React.Dispatch<React.SetStateAction<any>> }
type Choice = { label:string; value:string }

const groups:{key:string; title:string; hint:string; choices:Choice[]}[] = [
  { key:'time', title:'今天准备逛多久？', hint:'路线会根据时间自动控制节点数量', choices:[{label:'1小时内',value:'只有1小时'},{label:'2小时左右',value:'只有2小时'},{label:'半天',value:'有半天时间'},{label:'全天慢慢逛',value:'有一整天时间'}] },
  { key:'company', title:'今天和谁一起？', hint:'同行人会影响节奏、休息和讲解方式', choices:[{label:'自己一个人',value:'我一个人'},{label:'和朋友',value:'和朋友一起'},{label:'亲子出行',value:'带着孩子'},{label:'长辈同行',value:'和长辈一起'}] },
  { key:'pace', title:'今天想用什么节奏？', hint:'不用精确评估，凭第一感觉选择', choices:[{label:'轻松省力',value:'想轻松一点，不想爬山'},{label:'边走边看',value:'边走边看，不赶时间'},{label:'动物优先',value:'想尽可能多看动物'},{label:'探索路线',value:'想走一条有探索感的路线'}] },
  { key:'want', title:'今天最想去哪里？', hint:'可以多选，也可以选择“都不是”后补充', choices:[{label:'熊猫馆',value:'今天很想去熊猫馆'},{label:'貉 / 本土物种',value:'想去本土物种保育区看看貉'},{label:'灵长馆',value:'今天想去亚洲灵长馆'},{label:'湿地生态',value:'想去湿地生态区'}] },
  { key:'avoid', title:'有什么需要我避开？', hint:'没有就跳过；之后仍可在游玩中调整', choices:[{label:'怕晒',value:'怕晒，优先树荫'},{label:'不想爬坡',value:'不想爬山或爬坡'},{label:'需要休息',value:'中途需要休息'},{label:'避开拥挤',value:'尽量避开拥挤'}] },
]

export default function PlanV6({s,setS}:Props){
  const [selected,setSelected]=useState<Record<string,string[]>>({})
  const [skipped,setSkipped]=useState<string[]>([])
  const [extra,setExtra]=useState('')
  const [active,setActive]=useState(0)
  const [loading,setLoading]=useState(false)
  const [status,setStatus]=useState('')
  const [recording,setRecording]=useState(false)
  const toggle=(key:string,value:string)=>{setSkipped(v=>v.filter(x=>x!==key));setSelected(v=>({...v,[key]:v[key]?.includes(value)?v[key].filter(x=>x!==value):[...(v[key]||[]),value]}))}
  const summary=useMemo(()=>Object.values(selected).flat().join('；')+(extra?`；${extra}`:''),[selected,extra])
  const submit=async()=>{if(!summary){setStatus('先选择一个方向，或补充告诉我今天想怎么逛');return};setLoading(true);setStatus('正在理解你的需求并计算路线…');try{const text=summary;const result=await planRoute({natural_language:text,preferences:{duration_minutes:summary.includes('1小时')?60:summary.includes('半天')?240:summary.includes('一整天')?480:120,pace:summary.includes('省力')?'slow':summary.includes('探索')?'challenge':'balanced',avoid_climbing:summary.includes('爬山')||summary.includes('爬坡'),avoid_sun:summary.includes('怕晒'),with_child:summary.includes('孩子'),preferred_animals:summary.includes('熊猫')?['大熊猫']:[],must_visit:summary.includes('熊猫')?['panda']:[]}});setS((v:any)=>({...v,page:'route',preference:text,routeMode:result.route.route_mode==='effort_saving'?'省力优先线':v.routeMode}))}catch{setStatus('路线服务暂不可用，已保留你的需求并进入演示路线');setTimeout(()=>setS((v:any)=>({...v,page:'route',preference:summary})),500)}finally{setLoading(false)}}
  const group=groups[active]
  const startVoice=()=>{const w=window as any;const SpeechRecognition=w.SpeechRecognition||w.webkitSpeechRecognition;if(!SpeechRecognition){setStatus('当前浏览器不支持语音输入，请使用 Chrome 或 Edge，或直接输入文字');return}if(recording){setRecording(false);return}const recognition=new SpeechRecognition();recognition.lang='zh-CN';recognition.interimResults=false;recognition.continuous=false;setRecording(true);setStatus('正在听，请说出你想补充的需求…');recognition.onresult=(event:any)=>{const transcript=event.results?.[0]?.[0]?.transcript||'';if(transcript)setExtra(v=>(v?`${v}；`:'')+transcript);setStatus(`已听到：“${transcript}”`)};recognition.onerror=()=>setStatus('没有听清，可以再点一次麦克风');recognition.onend=()=>setRecording(false);recognition.start()}
  return <div className="page plan-form interactive-plan"><div className="form-head"><p className="eyebrow">ROUTE AGENT · 需求共创</p><h1>今天想怎么逛红山？</h1><p>先选几个方向，不合适的地方可以随时补充。</p></div><div className="need-summary"><div className="summary-head"><Sparkles size={16}/><b>我正在了解你的今天</b><span>{Object.values(selected).flat().length} 项已选择</span></div><div className="summary-tags">{Object.values(selected).flat().map(x=><span key={x}>{x}<button onClick={()=>{for(const g of groups){if(selected[g.key]?.includes(x))toggle(g.key,x)}}}><X size={11}/></button></span>)}{!summary&&<small>还没有填写，先从下面选一个吧</small>}</div></div><div className="need-progress">{groups.map((g,i)=><button key={g.key} className={i===active?'active':''} onClick={()=>setActive(i)}><i>{selected[g.key]?.length?<Check size={12}/>:skipped.includes(g.key)?'—':i+1}</i>{g.title.replace('今天','')}</button>)}</div><div className="choice-panel"><div className="choice-title"><div><h2>{group.title}</h2><p>{skipped.includes(group.key)?'这一项已暂不填写，之后仍可点击上方步骤补充。':group.hint}</p></div>{active>0&&<button className="text-btn" onClick={()=>setActive(active-1)}>上一步</button>}</div><div className="choice-grid">{group.choices.map(c=><button key={c.value} className={selected[group.key]?.includes(c.value)?'selected':''} onClick={()=>toggle(group.key,c.value)}><span>{selected[group.key]?.includes(c.value)?<Check size={15}/>:<Plus size={15}/>}</span>{c.label}</button>)}</div><div className="choice-actions"><button className="skip-choice" onClick={()=>setSkipped(v=>v.includes(group.key)?v.filter(x=>x!==group.key):[...v,group.key])}>{skipped.includes(group.key)?'取消暂不填写':'这一项先不填'}</button><button className="next-choice" onClick={()=>setActive(Math.min(groups.length-1,active+1))}>{active===groups.length-1?'回顾需求':'下一项'} <ArrowRight size={14}/></button></div></div><div className="extra-box"><div><button className={`voice-input-btn ${recording?'recording':''}`} onClick={startVoice} aria-label="语音输入"><Mic size={17}/></button><b>{recording?'正在听…':'还想补充什么？'}</b><small>比如“想看一场讲解”“不想走回头路”</small></div><textarea value={extra} onChange={e=>setExtra(e.target.value)} placeholder={recording?'请说出你想补充的需求…':'把选择里没有覆盖的需求告诉我…'} maxLength={160}/><span>{extra.length}/160</span></div>{status&&<div className="api-status"><Sparkles size={15}/>{status}</div>}<button className="primary full" disabled={loading} onClick={submit}>{loading?'正在生成…':'生成我的专属路线'} <ArrowRight size={17}/></button><p className="privacy">你可以在游玩过程中继续告诉搭子要休息、避开拥挤或临时改变目的地</p></div>
}

from dataclasses import dataclass
import networkx as nx
from .park_data import EDGES, POIS
from .schemas import Preferences

@dataclass
class RouteResult:
    ordered_pois:list[str]
    legs:list[dict]
    total_distance_m:int
    walking_minutes:int
    stay_minutes:int
    reasons:list[str]

def graph_for(pref:Preferences)->nx.Graph:
    g=nx.Graph()
    for a,b,d,s,shade,crowd in EDGES:
        if a in pref.avoid_pois or b in pref.avoid_pois:continue
        # cost is minutes plus preference penalties, not an LLM guess
        cost=d/70+s*(20 if pref.avoid_climbing else 5)+(1-shade)*(16 if pref.avoid_sun else 2)+crowd*(12 if pref.with_child else 7)
        g.add_edge(a,b,cost=cost,distance=d,walking=max(1,round(d/70)),slope=s,shade=shade,crowd=crowd)
    return g

def shortest(g:nx.Graph,start:str,end:str):
    try:return nx.shortest_path(g,start,end,weight='cost')
    except (nx.NetworkXNoPath,nx.NodeNotFound):return []

def path_cost(g:nx.Graph,path:list[str])->float:
    return sum(g[a][b]['cost'] for a,b in zip(path,path[1:]))

def calculate(pref:Preferences,status:dict|None=None)->RouteResult:
    g=graph_for(pref);start=pref.start_poi;end=pref.end_poi
    budget=max(30,pref.duration_minutes)
    # 动物福利优先于必去约束：医疗/喂养/休息等不宜打扰状态的场馆强制屏蔽，不进任何路线。
    welfare_ok=lambda x:POIS[x].open and POIS[x].welfare_status=='open'
    shielded=[x for x in pref.must_visit if x in POIS and POIS[x].open and not welfare_ok(x)]
    must=list(dict.fromkeys([x for x in pref.must_visit if x in POIS and welfare_ok(x) and x not in pref.avoid_pois]))
    for animal in pref.preferred_animals:
        if '熊猫' in animal and 'panda' not in must:must.append('panda')
        if '灵长' in animal and 'primate' not in must:must.append('primate')
        if '貉' in animal and 'native' not in must:must.append('native')
    candidates=[x for x in POIS if POIS[x].category in {'panda','native','primate','africa'} and x not in must and x not in pref.avoid_pois and welfare_ok(x)]
    def score(x):
        p=POIS[x]; value=p.active*3+(p.shade if pref.avoid_sun else 0)+(1-p.crowd if pref.with_child else 0)
        if x in must:value+=100
        return value
    candidates.sort(key=score,reverse=True)
    chosen=[];cur=start;used=0
    for poi in must+candidates:
        if poi in chosen:continue
        path=shortest(g,cur,poi)
        if not path:continue
        travel=sum(g[a][b]['walking'] for a,b in zip(path,path[1:]))
        rest_extra=12 if pref.with_child and 'rest' not in chosen and poi!='rest' else 0
        reserve_path=shortest(g,poi,end)
        reserve=sum(g[a][b]['walking'] for a,b in zip(reserve_path,reserve_path[1:])) if reserve_path else 999
        if used+travel+POIS[poi].stay_minutes+rest_extra+reserve>budget and poi not in must:continue
        chosen.append(poi);used+=travel+POIS[poi].stay_minutes;cur=poi
        if pref.with_child and 'rest' not in chosen and poi!='rest' and used+12<=budget:
            chosen.append('rest');used+=12;cur='rest'
    route=[start];cur=start
    for poi in chosen:
        path=shortest(g,cur,poi)
        if path:route+=path[1:];cur=poi
    path=shortest(g,cur,end)
    if path:route+=path[1:]
    compact=[]
    for node in route:
        if not compact or compact[-1]!=node:compact.append(node)
    legs=[];distance=walk=stay=0
    for a,b in zip(compact,compact[1:]):
        edge=g[a][b];distance+=edge['distance'];walk+=edge['walking'];legs.append({'from':a,'to':b,'distance_m':edge['distance'],'walking_minutes':edge['walking'],'shade':edge['shade'],'crowd':edge['crowd']})
    for node in chosen:stay+=POIS[node].stay_minutes
    reasons=['Qwen提取需求，路线引擎在园区拓扑图上计算路径','按步行距离、坡度、树荫、拥挤度和停留时间综合评分']
    if pref.avoid_climbing:reasons.append('降低坡度较高道路的权重')
    if pref.avoid_sun:reasons.append('优先选择树荫覆盖较高的道路')
    if pref.with_child:reasons.append('控制连续步行时间并插入休息点')
    if must:reasons.append('保留明确指定的必去节点：'+', '.join(POIS[x].name for x in must))
    if shielded:reasons.append('按动物福利要求屏蔽了不宜打扰状态的场馆：'+', '.join(POIS[x].name for x in shielded))
    return RouteResult([start]+chosen+[end],legs,distance,walk,stay,reasons)

def serialize(result:RouteResult,pref:Preferences,route_id='route_live'):
    total=result.walking_minutes+result.stay_minutes
    visible=[]
    for x in result.ordered_pois:
        if POIS[x].category!='junction' and x not in visible:visible.append(x)
    return {'route_id':route_id,'route_mode':'effort_saving' if pref.pace=='slow' else 'interest_first' if pref.pace=='challenge' else 'balanced','planning_method':'weighted_graph_dijkstra','data_source':'official_map_topology_v1','start_time':'09:30','end_time':f'{9+((30+total)//60):02d}:{(30+total)%60:02d}','ordered_pois':[{'id':x,'name':POIS[x].name,'stay_minutes':POIS[x].stay_minutes} for x in visible],'legs':result.legs,'summary':{'total_distance_m':result.total_distance_m,'walking_minutes':result.walking_minutes,'stay_minutes':result.stay_minutes,'total_minutes':total,'budget_minutes':pref.duration_minutes},'reasons':result.reasons,'alternatives':[{'id':'effort_saving','label':'省力优先','tradeoff':'少走路、少爬坡，但可能减少节点'},{'id':'interest_first','label':'兴趣优先','tradeoff':'保留更多动物节点，可能更绕路'},{'id':'balanced','label':'平衡方案','tradeoff':'在兴趣与体力之间折中'}]}

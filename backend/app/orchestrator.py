from datetime import datetime
from .intent_agent import IntentAgent
from .route_engine import calculate, serialize
from .schemas import Preferences
from .park_data import POIS, park_snapshot
from .session_store import SESSIONS, create, get

class Orchestrator:
    def plan(self,text:str,pref:Preferences):
        parsed, source=IntentAgent().parse_with_qwen(text,pref); result=calculate(parsed); return {'intent':parsed.model_dump(),'route':serialize(result,parsed),'source':source}
    def start(self,route:dict): return create(route)
    def replan(self,sid:str,reason='',keep:list[str]|None=None):
        s=get(sid)
        if not s: return None
        keep=keep or []; old=s['route']; pref=Preferences(must_visit=keep,start_poi=s['current_location'],duration_minutes=max(30,s['remaining_minutes']))
        if reason in {'fatigue','hungry'}: pref.with_child=True; pref.avoid_climbing=True
        result=serialize(calculate(pref),pref,old['route_id']); s['route']=result; s['current_route']=[x['id'] for x in result['ordered_pois'][1:]]; s['last_replan_time']=datetime.now().isoformat(timespec='minutes'); return {'session':s,'adjustment':{'reason':reason,'preserved_pois':keep,'changed_from':old['ordered_pois'],'new_route':result['ordered_pois'],'message':self.message(reason)}}
    def event(self,sid:str,event_type:str,value=None,note=''):
        s=get(sid)
        if not s: return None
        s['events'].append({'type':event_type,'value':value,'note':note,'at':datetime.now().isoformat(timespec='minutes')})
        if event_type=='fatigue': s['fatigue_level']=str(value or 'slightly_tired'); return self.replan(sid,'fatigue')
        if event_type=='hungry': return self.replan(sid,'hungry',['food'])
        if event_type=='leave_early': return self.replan(sid,'leave_early',['south_gate'])
        if event_type=='crowd': return {'session':s,'adjustment':{'reason':'crowd','options':['continue_waiting','visit_nearby','skip_poi'],'message':'当前场馆拥挤，系统不会替你强行跳过，请选择节奏。'}}
        if event_type=='animal_active': return {'session':s,'adjustment':{'reason':'animal_active','options':['go_now','keep_plan'],'message':'动物活跃度出现变化，系统把它作为可选提醒，不承诺一定能看到。'}}
        return {'session':s,'adjustment':{'reason':event_type,'options':['keep_plan','replan'],'message':'已记录这次变化，建议先确认是否需要调整剩余路线。'}}
    @staticmethod
    def message(reason): return {'fatigue':'你走累了，系统插入最近休息点并降低后续坡度权重。','hungry':'已查找营业中的餐饮点，先补充能量再继续。','leave_early':'已锁定离园出口，压缩低优先级节点。'}.get(reason,'已根据当前状态更新剩余路线。')

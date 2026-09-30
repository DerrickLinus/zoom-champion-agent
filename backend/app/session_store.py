from datetime import datetime
from uuid import uuid4

SESSIONS:dict[str,dict] = {}
def create(route:dict)->dict:
    sid=f'sess_{uuid4().hex[:10]}'; now=datetime.now().isoformat(timespec='minutes'); s={'session_id':sid,'phase':'IN_VISIT','route_id':route['route_id'],'current_location':route['ordered_pois'][0]['id'],'current_index':0,'visited_pois':[route['ordered_pois'][0]['id']],'remaining_minutes':route['summary']['total_minutes'],'fatigue_level':'fresh','current_route':[x['id'] for x in route['ordered_pois'][1:]],'last_replan_time':now,'route':route,'events':[]}; SESSIONS[sid]=s; return s
def get(sid:str): return SESSIONS.get(sid)

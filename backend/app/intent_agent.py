import re
import time
from .bailian_client import BailianClient
from .schemas import Preferences

class IntentAgent:
    """Qwen extracts intent; local validation prevents the model from inventing POI ids."""
    ALLOWED={'panda','native','primate','rest','africa','food','north_gate','south_gate'}
    # preferred_animals 存中文类别名；若 Qwen 把 POI id 泄漏进来，这里做归一化。
    ANIMAL_LABELS={'primate':'灵长类','panda':'大熊猫','native':'貉','africa':'非洲动物','food':'餐饮','rest':'休息区'}

    def parse(self,text:str,base:Preferences)->Preferences:
        data=base.model_dump()
        if not text:return base
        if m:=re.search(r'(\d+)\s*(小时|h)',text,re.I):data['duration_minutes']=int(m.group(1))*60
        if '半天' in text:data['duration_minutes']=240
        if '全天' in text:data['duration_minutes']=480
        data['avoid_climbing']=data['avoid_climbing'] or any(x in text for x in ['不爬山','不想爬','怕累','省力','爬坡'])
        data['avoid_sun']=data['avoid_sun'] or any(x in text for x in ['怕晒','不想晒','避开太阳','树荫'])
        data['with_child']=data['with_child'] or any(x in text for x in ['孩子','宝宝','亲子','儿童'])
        if '熊猫' in text:data['preferred_animals']=list(dict.fromkeys(data['preferred_animals']+['大熊猫']));data['must_visit']=list(dict.fromkeys(data['must_visit']+['panda']))
        if '灵长' in text:data['preferred_animals']=list(dict.fromkeys(data['preferred_animals']+['灵长类']));data['must_visit']=list(dict.fromkeys(data['must_visit']+['primate']))
        if '貉' in text or '本土' in text:data['preferred_animals']=list(dict.fromkeys(data['preferred_animals']+['貉']));data['must_visit']=list(dict.fromkeys(data['must_visit']+['native']))
        if '休息' in text or '累' in text:data['must_visit']=list(dict.fromkeys(data['must_visit']+['rest']))
        return Preferences(**data)

    def parse_with_qwen(self,text:str,base:Preferences)->tuple[Preferences,str]:
        if not text:return base,'empty'
        client=BailianClient()
        system=('你是红山动物园路线需求解析器。只输出一个JSON对象，不要解释，不要Markdown。字段：'
                'duration_minutes, pace, avoid_climbing, avoid_sun, with_child, preferred_animals, must_visit, avoid_pois。约定：'
                'duration_minutes 为整数分钟，N小时=N*60，半天=240，全天=480；'
                'pace 取 slow/balanced/challenge；'
                'preferred_animals 用中文类别名，只能从这些里选：灵长类、大熊猫、貉、非洲动物；'
                'must_visit 和 avoid_pois 只能使用 POI id：panda,native,primate,rest,africa,food,north_gate,south_gate；'
                '用户明确想避开的场馆放进 avoid_pois，提到吃饭或用餐需求就在 must_visit 里加 food；'
                '用户没有提到的字段不要输出。')
        try:
            content=None
            for attempt in range(2):  # 限流/网络抖动退避重试一次，仍失败才降级规则解析
                try:
                    content=client.chat([
                        {'role':'system','content':system},
                        {'role':'user','content':f'已有偏好：{base.model_dump()}\n游客需求：{text}'}
                    ],temperature=0)
                    if content:break
                except Exception:
                    if attempt:raise
                    time.sleep(1.5)
            raw=client.parse_json(content)
            if raw:
                merged=base.model_dump()
                for key in ('duration_minutes','pace','avoid_climbing','avoid_sun','with_child','preferred_animals','must_visit','avoid_pois'):
                    if key in raw:merged[key]=raw[key]
                merged['must_visit']=[x for x in merged['must_visit'] if x in self.ALLOWED]
                merged['avoid_pois']=[x for x in merged['avoid_pois'] if x in self.ALLOWED]
                merged['preferred_animals']=list(dict.fromkeys(
                    self.ANIMAL_LABELS.get(str(x),str(x)) for x in merged['preferred_animals']))
                return Preferences(**merged),'qwen'
        except Exception:
            pass
        return self.parse(text,base),'rule_fallback'

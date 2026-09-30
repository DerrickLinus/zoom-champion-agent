import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

@dataclass(frozen=True)
class Poi:
    id: str
    name: str
    category: str
    stay_minutes: int
    slope: float
    shade: float
    crowd: float
    active: float
    open: bool = True
    welfare_status: str = 'open'

POIS = {
    'north_gate': Poi('north_gate','北门入口','gate',5,.10,.60,.35,0),
    'panda': Poi('panda','金陵大熊猫苑','panda',28,.35,.58,.72,.64),
    'native': Poi('native','本土物种保育区','native',24,.18,.80,.30,.58),
    'primate': Poi('primate','亚洲灵长馆','primate',22,.42,.72,.78,.82),
    'rest': Poi('rest','林间休息区','rest',12,.05,.92,.18,.10),
    'africa': Poi('africa','非洲之歌','africa',25,.50,.42,.45,.55),
    'food': Poi('food','林下餐饮点','food',30,.08,.75,.38,0),
    'south_gate': Poi('south_gate','南门出口','gate',5,.12,.55,.40,0),
    'east_gate': Poi('east_gate','东门出口','gate',5,.12,.48,.40,0),
    'north_junction': Poi('north_junction','北坡主路交叉点','junction',0,.18,.62,.35,0),
    'west_junction': Poi('west_junction','小红山西侧交叉点','junction',0,.20,.72,.30,0),
    'central_junction': Poi('central_junction','大红山中心交叉点','junction',0,.30,.60,.50,0),
    'east_junction': Poi('east_junction','东侧主路交叉点','junction',0,.22,.55,.55,0),
    'south_junction': Poi('south_junction','南侧服务区交叉点','junction',0,.16,.58,.40,0),
}

# v1 topology is transcribed from the official foldout map. Replace this table
# with surveyed GPS/polyline data when the zoo provides it.
_topology_path=Path(__file__).with_name('park_topology.json')
_topology=json.loads(_topology_path.read_text(encoding='utf-8'))
EDGES=[tuple(edge) for edge in _topology['edges']]

def poi_dict(poi:Poi)->dict: return asdict(poi)

def park_snapshot()->dict:
    return {'updated_at':datetime.now().astimezone().isoformat(timespec='minutes'),'data_source':'official_map_topology_v1','weather':{'label':'晴','temperature':29,'feels_like':31},'crowd_level':'simulated','pois':[poi_dict(p) for p in POIS.values()]}

def park_topology()->dict:
    return _topology

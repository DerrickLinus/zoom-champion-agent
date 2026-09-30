"""Latency benchmark for the deterministic route engine (no LLM involved)."""
import json, time, statistics, httpx

BASE = 'http://127.0.0.1:8765'
client = httpx.Client(timeout=30)

CASES = {
    'plan_2h_child_sunny':  {'natural_language': '我带着3岁孩子，只有2小时，怕晒，不想爬山，想看灵长类',
                             'preferences': {'duration_minutes': 120, 'pace': 'slow', 'avoid_climbing': True, 'avoid_sun': True, 'with_child': True, 'preferred_animals': ['灵长类'], 'must_visit': []}},
    'plan_1h_fast':         {'natural_language': '只有一个小时，随便逛逛',
                             'preferences': {'duration_minutes': 60, 'pace': 'balanced', 'avoid_climbing': False, 'avoid_sun': False, 'with_child': False, 'preferred_animals': [], 'must_visit': []}},
    'plan_fullday_must':    {'natural_language': '玩一整天，必去熊猫馆和本土区，避开非洲区',
                             'preferences': {'duration_minutes': 480, 'pace': 'challenge', 'avoid_climbing': False, 'avoid_sun': True, 'with_child': False, 'preferred_animals': ['大熊猫'], 'must_visit': ['panda', 'native'], 'avoid_pois': ['africa']}},
}

def pct(sorted_vals, p):
    idx = min(len(sorted_vals)-1, round(p/100 * (len(sorted_vals)-1)))
    return sorted_vals[idx]

all_lat = []
for name, body in CASES.items():
    lat = []
    for i in range(60):
        t0 = time.perf_counter()
        r = client.post(f'{BASE}/api/route/plan', json=body)
        r.raise_for_status()
        lat.append((time.perf_counter()-t0)*1000)
    lat.sort(); all_lat += lat
    result = r.json()
    print(f"{name:24s} n={len(lat)} P50={pct(lat,50):6.1f}ms P95={pct(lat,95):6.1f}ms max={lat[-1]:6.1f}ms  pois={[p['name'] for p in result['route']['ordered_pois']]}")

# session + event-driven replan latency
r = client.post(f'{BASE}/api/session/start', json={'route_id': 'route_live'})
sid = r.json()['session_id']
ev_lat = []
for i in range(40):
    t0 = time.perf_counter()
    r = client.post(f'{BASE}/api/session/event', json={'session_id': sid, 'event_type': 'fatigue', 'value': 'tired'})
    r.raise_for_status()
    ev_lat.append((time.perf_counter()-t0)*1000)
ev_lat.sort()
print(f"{'event_replan(fatigue)':24s} n={len(ev_lat)} P50={pct(ev_lat,50):6.1f}ms P95={pct(ev_lat,95):6.1f}ms max={ev_lat[-1]:6.1f}ms")

all_lat.sort()
print(f"\nALL PLAN CALLS: n={len(all_lat)} P50={pct(all_lat,50):.1f}ms P95={pct(all_lat,95):.1f}ms max={all_lat[-1]:.1f}ms")
# sanity: verify constraints hold on a sample plan
r = client.post(f'{BASE}/api/route/plan', json=CASES['plan_2h_child_sunny']).json()
print(f"\nsample plan: mode={r['route']['route_mode']} total={r['route']['summary']['total_minutes']}min budget={r['route']['summary']['budget_minutes']}min distance={r['route']['summary']['total_distance_m']}m")

"""路线引擎与游中调整的约束回归测试。

跑法：cd backend && .venv/bin/python -m pytest
不依赖任何 API Key——被测对象是确定性核心（图算法 + 状态机），这正是混合架构
"LLM 只做理解与解释、决策核心可验证可复现"的回归保障。
"""
from __future__ import annotations

from app.orchestrator import Orchestrator
from app.park_data import POIS
from app.route_engine import calculate, serialize
from app.schemas import Preferences


def visible_ids(result: dict) -> list[str]:
    return [p["id"] for p in result["ordered_pois"]]


def test_budget_never_exceeded_without_must_visit():
    """无必去场馆时，路线总时长（步行+停留）不得超过时间预算。"""
    for budget in (30, 60, 120, 240, 480):
        pref = Preferences(duration_minutes=budget, avoid_climbing=False,
                           avoid_sun=False, with_child=False)
        result = serialize(calculate(pref), pref)
        assert result["summary"]["total_minutes"] <= budget, f"budget={budget}"


def test_must_visit_always_kept():
    """必去场馆在任何预算下都必须出现在路线中。"""
    pref = Preferences(duration_minutes=60, must_visit=["panda", "native"],
                       avoid_climbing=False, avoid_sun=False, with_child=False)
    ids = visible_ids(serialize(calculate(pref), pref))
    assert {"panda", "native"} <= set(ids)


def test_avoid_pois_never_planned():
    pref = Preferences(avoid_pois=["africa"], avoid_climbing=False,
                       avoid_sun=False, with_child=False)
    ids = visible_ids(serialize(calculate(pref), pref))
    assert "africa" not in ids


def test_invalid_poi_ids_dropped_not_crashed():
    """来自 LLM 的非法 POI id 会被拓扑表过滤掉，而不是进入路线或抛错。"""
    pref = Preferences(must_visit=["panda", "disneyland", ""],
                       avoid_climbing=False, avoid_sun=False, with_child=False)
    ids = visible_ids(serialize(calculate(pref), pref))
    assert "panda" in ids and "disneyland" not in ids


def test_with_child_inserts_rest_point():
    pref = Preferences(duration_minutes=240, with_child=True,
                       avoid_climbing=False, avoid_sun=False)
    ids = visible_ids(serialize(calculate(pref), pref))
    assert "rest" in ids, "亲子路线应主动插入休息节点"


def test_legs_form_connected_walk():
    """输出的每一段 leg 都必须是园区拓扑中真实相邻的节点。"""
    from app.route_engine import graph_for
    pref = Preferences(avoid_climbing=False, avoid_sun=False, with_child=False)
    g = graph_for(pref)
    result = serialize(calculate(pref), pref)
    for leg in result["legs"]:
        assert g.has_edge(leg["from"], leg["to"]), leg


def test_welfare_status_blocks_even_must_visit(monkeypatch):
    """动物福利优先于必去约束：医疗/喂养/休息状态场馆强制屏蔽，被指定必去也不进路线。"""
    from dataclasses import replace

    import app.route_engine as route_module

    blocked = dict(route_module.POIS)
    blocked["panda"] = replace(blocked["panda"], welfare_status="medical")
    monkeypatch.setattr(route_module, "POIS", blocked)
    pref = Preferences(must_visit=["panda", "native"], avoid_climbing=False,
                       avoid_sun=False, with_child=False)
    result = serialize(route_module.calculate(pref), pref)
    ids = visible_ids(result)
    assert "panda" not in ids, "医疗状态场馆必须被强制屏蔽"
    assert "native" in ids, "正常场馆不受影响"
    assert any("动物福利" in r for r in result["reasons"]), "屏蔽行为必须出现在推荐理由里"


def test_event_replan_keeps_session_and_returns_adjustment():
    """游中事件触发局部重规划：session 存活、调整说明返回、剩余时间作为新预算。"""
    orch = Orchestrator()
    planned = orch.plan("", Preferences(avoid_climbing=False, avoid_sun=False, with_child=False))
    session = orch.start(planned["route"])
    sid = session["session_id"]
    out = orch.event(sid, "fatigue", value="tired")
    assert out is not None
    assert out["session"]["session_id"] == sid
    assert out["adjustment"]["reason"] == "fatigue"
    assert out["adjustment"]["new_route"], "重规划必须返回新的剩余路线"
    assert out["session"]["visited_pois"], "已访问节点不应被清空"


def test_replan_budget_uses_remaining_time():
    """重规划的时间预算取自 session 剩余时间，而不是原始预算。"""
    orch = Orchestrator()
    planned = orch.plan("", Preferences(duration_minutes=120, avoid_climbing=False,
                                        avoid_sun=False, with_child=False))
    session = orch.start(planned["route"])
    session["remaining_minutes"] = 45
    out = orch.replan(session["session_id"], reason="fatigue")
    assert out["session"]["route"]["summary"]["total_minutes"] <= 45

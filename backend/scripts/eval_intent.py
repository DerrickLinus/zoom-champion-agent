"""意图解析评测：标注测试集 → IntentAgent → 字段级准确率。

用法：
    cd backend
    .venv/bin/python scripts/eval_intent.py            # 无 API Key 时测规则兜底路径
    DASHSCOPE_API_KEY=sk-xxx .venv/bin/python scripts/eval_intent.py   # 测 Qwen 路径

每条用例在"中性偏好底座"上评测（avoid_climbing/avoid_sun/with_child 默认 False），
避免 schemas 里的业务默认值干扰抽取准确率统计。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:  # 读取 backend/.env 中的 DASHSCOPE_API_KEY（文件本身被 gitignore）
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

if not os.getenv("DASHSCOPE_API_KEY"):
    print("提示：未检测到 DASHSCOPE_API_KEY，本次只评测规则兜底路径。\n")

from app.intent_agent import IntentAgent  # noqa: E402
from app.schemas import Preferences  # noqa: E402

# 期望字段只写"从这句话里可无争议推出"的结论；不写的字段不参与评分。
CASES: list[dict] = [
    {"text": "我带着3岁孩子，只有2小时，怕晒，不想爬山，想看灵长类",
     "expect": {"duration_minutes": 120, "avoid_sun": True, "avoid_climbing": True,
                "with_child": True, "preferred_animals": ["灵长类"]}},
    {"text": "就一个钟头，随便走走看看",
     "expect": {"duration_minutes": 60, "with_child": False}},
    {"text": "打算玩一整天，重点看大熊猫",
     "expect": {"duration_minutes": 480, "must_visit": ["panda"]}},
    {"text": "下午遛娃两小时，最好别暴晒",
     "expect": {"duration_minutes": 120, "with_child": True, "avoid_sun": True}},
    {"text": "腿脚不太方便，不想爬坡",
     "expect": {"avoid_climbing": True}},
    {"text": "特别怕晒，想多走在树荫里",
     "expect": {"avoid_sun": True}},
    {"text": "想看本土物种，貉啊獐啊这些",
     "expect": {"preferred_animals": ["貉"], "must_visit": ["native"]}},
    {"text": "必须去熊猫馆，其他随意安排",
     "expect": {"must_visit": ["panda"]}},
    {"text": "推着婴儿车，找个好走的路线",
     "expect": {"with_child": True}},
    {"text": "两个小时吧，孩子想看猴子",
     "expect": {"duration_minutes": 120, "with_child": True, "preferred_animals": ["灵长类"]}},
    {"text": "半天时间，轻松一点，怕累",
     "expect": {"duration_minutes": 240}},
    {"text": "对非洲动物感兴趣，体力没问题",
     "expect": {"preferred_animals": ["非洲动物"], "avoid_climbing": False}},
    {"text": "上次非洲区去过了，这次避开",
     "expect": {"avoid_pois": ["africa"]}},
    {"text": "中途需要休息一下，带孩子走不了太久",
     "expect": {"with_child": True}},
    {"text": "3小时，先看熊猫再随便逛",
     "expect": {"duration_minutes": 180, "must_visit": ["panda"]}},
    {"text": "我怕热，晒不得",
     "expect": {"avoid_sun": True}},
    {"text": "挑战一下自己，把需要爬坡的馆都走了",
     "expect": {"avoid_climbing": False}},
    {"text": "两个半小时，想去有遮荫的地方",
     "expect": {"duration_minutes": 150, "avoid_sun": True}},
    {"text": "带孩子，想找个地方吃东西",
     "expect": {"with_child": True}},
    {"text": "快速逛一圈，一个小时够了，别安排爬山的",
     "expect": {"duration_minutes": 60, "avoid_climbing": True}},
    {"text": "老人家一起，走平路，两小时",
     "expect": {"duration_minutes": 120, "avoid_climbing": True}},
    {"text": "想看猴子一家，顺便吃个午饭",
     "expect": {"preferred_animals": ["灵长类"]}},
    {"text": "没什么特别要求，两小时轻松逛",
     "expect": {"duration_minutes": 120}},
    {"text": "烈日当头，防晒第一，看什么动物都行",
     "expect": {"avoid_sun": True}},
]

BOOL_FIELDS = ("avoid_climbing", "avoid_sun", "with_child")


def neutral_base() -> Preferences:
    return Preferences(avoid_climbing=False, avoid_sun=False, with_child=False,
                       preferred_animals=[], must_visit=[], avoid_pois=[])


def score_case(parsed: Preferences, expect: dict) -> tuple[int, int, list[str]]:
    """返回 (正确字段数, 参评字段数, 错误明细)。"""
    got = parsed.model_dump()
    correct = total = 0
    errors: list[str] = []
    for field, want in expect.items():
        total += 1
        have = got.get(field)
        if field in BOOL_FIELDS:
            ok = bool(have) == bool(want)
        elif isinstance(want, list):
            have_set = {str(x) for x in (have or [])}
            want_set = {str(x) for x in want}
            # 期望项全部命中即可：模型多识别出的合理需求（如"想吃午饭"→food）不算错。
            ok = want_set.issubset(have_set)
        else:
            ok = have == want
        if ok:
            correct += 1
        else:
            errors.append(f"{field}: expect={want!r} got={have!r}")
    return correct, total, errors


def main() -> None:
    import time
    agent = IntentAgent()
    per_source: dict[str, list[float]] = {}
    failures: list[tuple[str, str, list[str]]] = []
    for index, case in enumerate(CASES):
        if index:
            time.sleep(0.6)  # 连续调用避免触发限流，保证测量稳定
        parsed, source = agent.parse_with_qwen(case["text"], neutral_base())
        correct, total, errors = score_case(parsed, case["expect"])
        per_source.setdefault(source, []).append(correct / total if total else 1.0)
        if errors:
            failures.append((case["text"], source, errors))

    print(f"测试集：{len(CASES)} 条 · 逐字段评分（列表字段按集合比较）")
    overall = []
    for source, scores in per_source.items():
        avg = sum(scores) / len(scores)
        overall += scores
        print(f"  解析路径 {source:14s} n={len(scores):2d} 字段准确率 {avg:6.1%}")
    print(f"  整体字段准确率 {sum(overall) / len(overall):6.1%}")
    if failures:
        print("\n失败明细：")
        for text, source, errors in failures:
            print(f"  [{source}] {text}")
            for err in errors:
                print(f"      {err}")


if __name__ == "__main__":
    main()

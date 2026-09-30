"""百炼驱动的游伴问答与故事 Agent。"""
from __future__ import annotations

from typing import Any

from .bailian_client import BailianClient

FACTS = {
    "敲玻璃": "敲击玻璃会惊扰动物，也可能让动物把玻璃和威胁联系起来。请保持安静，用耐心观察代替敲击。",
    "投喂": "园区动物有专业的饲养方案，游客投喂可能造成营养和行为问题，请不要投喂。",
    "貉": "貉是南京常见的本土野生动物，通常在清晨或黄昏更活跃。实时状态以现场公告为准。",
    "动物福利": "红山强调动物优先，展陈和游览都应优先保障动物的安全、健康和自主选择。",
}

STYLE_LABELS = {
    "detective": "森林侦探",
    "rescue": "动物救援",
    "archive": "时空档案馆",
    "treasure": "森林宝藏",
    "growth": "搭子成长冒险",
    "comedy": "轻喜剧闯关",
}

STYLE_RULES = {
    "detective": "每个节点提供一个证人、现场细节或矛盾证词，最后让游客还原真相。",
    "rescue": "搭子发现伙伴失联，游客收集声音、食物痕迹、脚印和栖息地线索，但不能追逐或投喂。",
    "archive": "一张旧地图缺少五段记忆，每到一个真实路线节点补回一段园区时间。",
    "treasure": "每个 NPC 任务获得一块森林印记，印记拼成下一站线索和最终纪念品兑换提示。",
    "growth": "每个节点给游客一个相处选择，搭子会记住选择，最终生成体现关系变化的结局。",
    "comedy": "搭子闯下一个无害的小麻烦，游客通过 NPC 任务逐站补救，保持轻松、有画面感。",
}


COMPANION_PERSONAS = {
    "\u56e2\u56e2": "你是团团，小熊猫式慢游伴。语气温柔、慢一点、像把游客带到树荫下的朋友。先邀请观察，再给答案；经常提醒停留、倾听和不打扰。不要催促用户打卡。",
    "\u8c89\u5c0f\u6ee1": "你是貉小满，本土物种观察员。语气机灵、好奇、带一点侦探感。关注城市里容易被忽略的动物痕迹、黄昏活动和生境边缘，回答时多抛出一个可验证的观察问题。",
    "\u9ea6\u7a57": "你是麦穗，赤狐边界漫游者。语气独立、克制、清醒，句子短一些。重视距离、边界和动物自主选择，遇到追逐、投喂、敲玻璃时明确制止，并给出温和替代动作。",
    "\u7360\u706f": "你是獐灯，湿地轻声向导。语气安静、细腻，擅长把声音、水面、植物和动物行为串成生态关系。少用夸张形容，多引导游客降低音量、等待和辨认变化。",
}
DEFAULT_COMPANION_PERSONA = "你是红山森林动物园的温和游伴。请根据现场点位引导用户观察，不把动物当成表演对象，优先提醒尊重距离和动物福利。"

class CompanionAgent:
    def __init__(self) -> None:
        self.client = BailianClient()

    def answer(self, question: str, context: str = "", companion: str = "小红", language: str = "zh-CN") -> tuple[str, str]:
        matched = [value for key, value in FACTS.items() if key in question]
        retrieved = "\n".join(matched) or "没有检索到直接匹配的官方片段；不要编造事实，实时开放和动物状态以现场公告为准。"
        try:
            output_language = "English" if language.lower().startswith("en") else "简体中文"
            companion_persona = COMPANION_PERSONAS.get(companion, DEFAULT_COMPANION_PERSONA)
            text = self.client.chat([
                {"role": "system", "content": f"Companion Persona: {companion_persona}"},
                {"role": "system", "content": f"你是南京红山森林动物园的有温度智能游伴。优先依据官方片段回答，不确定就明确说不知道。回答控制在120字内，适合手机阅读和语音朗读。请始终使用{output_language}回答；不要把虚构故事当成官方事实。"},
                {"role": "user", "content": f"搭子：{companion}\n当前场景：{context}\n官方片段：{retrieved}\n游客问题：{question}"},
            ], temperature=0.35)
            if text:
                return text, "bailian_rag" if matched else "bailian"
        except Exception:
            pass
        for key, value in FACTS.items():
            if key in question:
                return value, "local_knowledge"
        return "我先把这个问题记进线索册啦。关于实时开放和动物状态，请以园区现场公告为准。", "fallback"

    def story(self, payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
        style = str(payload.get("style") or "detective")
        if style not in STYLE_LABELS:
            style = "detective"
        route = payload.get("route") or []
        # The story must follow the route returned by the planner. Do not cap or
        # replace user-selected points here; the number of chapters is route-driven.
        route_names = [str(item.get("name", item)) for item in route]
        chapter_count = len(route_names) if route_names else 0
        companion_persona = COMPANION_PERSONAS.get(str(payload.get("companion") or ""), DEFAULT_COMPANION_PERSONA)
        route_signature = " → ".join(route_names) or "园区入口 → 林间路线"
        route_theme = self._route_theme(route_names)
        route_text = "、".join(route_names) or str(payload.get("current_poi") or "园区入口")
        companion = str(payload.get("companion") or "你的搭子")
        clues = payload.get("collected_clues") or []
        npc = payload.get("completed_npcs") or []
        persona = payload.get("persona") or {}
        system = f"""你是红山森林动物园的沉浸式故事总编。故事必须围绕真实游玩路线展开，不能写成泛泛童话。
故事模式：{STYLE_LABELS[style]}。模式规则：{STYLE_RULES[style]}
这条路线的独特主题是：{route_theme}。路线顺序是：{route_signature}。标题和 hook 必须体现这条路线的节点组合，不能套用另一条路线的故事。
必须遵守：官方动物事实不能编造；可以虚构任务、角色和叙事，但不要声称虚构事件是园方事实；不要让游客接触、投喂、追逐动物。必须根据用户身份和搭子关系阶段改变叙事语气与任务难度。
请只输出 JSON，不要 Markdown，字段必须是：title, subtitle, hook, core_mystery, chapters, ending, possible_endings, modeLabel。
chapters 必须是 {chapter_count} 个对象，每个对象字段：point, label, scene, clue, npc_task, choices, next_hint, action。point 必须来自给定路线节点，章节顺序不能改变。
每章 scene 80-150 字，要有具体现场细节、线索推进和下一站动机；choices 必须是 2 个对象，每个对象包含 id、label、effect；choice 的 effect 要改变用户对谜题的判断或搭子态度，而不是无意义的按钮。
每章必须让用户做一件可在现场完成的观察或 NPC 任务。不要把动物事实写成虚构事件。结局要根据用户选择可能出现不同方向，并回收开场悬念。"""
        user = {
            "companion": companion,
            "route_points": route_names,
            "companion_persona": companion_persona,
            "collected_clues": clues,
            "completed_npcs": npc,
            "style": style,
            "persona": persona,
            "route_signature": route_signature,
            "route_theme": route_theme,
        }
        try:
            raw = self.client.chat([
                {"role": "system", "content": system},
                {"role": "user", "content": str(user)},
            ], temperature=0.72)
            parsed = self.client.parse_json(raw)
            if chapter_count and parsed and isinstance(parsed.get("chapters"), list) and len(parsed["chapters"]) >= chapter_count:
                parsed["chapters"] = parsed["chapters"][:chapter_count]
                # 模型负责写内容，节点归属由路线引擎负责，防止模型编造不存在的场馆。
                if route_names:
                    for index, chapter in enumerate(parsed["chapters"]):
                        chapter["point"] = route_names[index]
                        chapter.setdefault("scene", chapter.get("text", ""))
                        chapter.setdefault("clue", "一处需要继续观察的现场细节")
                        chapter.setdefault("npc_task", chapter.get("action", "完成一次安静观察"))
                        chapter.setdefault("choices", [{"id":"observe", "label":"继续观察", "effect":"保留当前线索"}, {"id":"trust", "label":"相信搭子", "effect":"提高搭子信任"}])
                        chapter.setdefault("next_hint", "把这条线索带到下一站")
                        chapter.setdefault("action", chapter.get("npc_task", "完成一次安静观察"))
                    parsed["subtitle"] = f"{parsed.get('subtitle', STYLE_LABELS[style])} · {route_theme}"
                    parsed["hook"] = f"{parsed.get('hook', '')} 这条路线依次经过：{route_signature}。"
                return parsed, "bailian_story_agent"
        except Exception:
            pass
        return self._fallback_story(style, companion, route_names, clues, npc, route_theme), "local_story_fallback"

    @staticmethod
    def _route_theme(route: list[str]) -> str:
        text = " ".join(route)
        if "熊猫" in text and "灵长" in text:
            return "从熊猫馆的独处观察走向灵长馆的群体关系"
        if "非洲" in text:
            return "从非洲生境的开阔感走向园区不同动物的生活边界"
        if "本土" in text or "貉" in text or "獐" in text:
            return "从城市本土动物的痕迹走向不打扰的生境观察"
        if "休息" in text or "林间" in text:
            return "从行走和停留的节奏中听见森林的层次"
        return "从入口逐步建立与动物和生境的观察关系"

    def _fallback_story(self, style: str, companion: str, route: list[str], clues: list[str], npc: list[str], route_theme: str) -> dict[str, Any]:
        points = route[:] if route and all(isinstance(item, str) for item in route) else route_names[:] if route_names else ["园区入口", "金陵大熊猫苑", "本土物种保育区", "亚洲灵长馆", "出口"]
        labels = {
            "detective": ["案件受理", "现场证词", "矛盾出现", "关键转折", "案件结案"],
            "rescue": ["发现失联", "寻找声音", "追踪痕迹", "确认生境", "安全回信"],
            "archive": ["获得旧图", "翻开档案", "对照记忆", "补上缺页", "归还档案"],
            "treasure": ["领取空印", "第一枚印记", "NPC 试炼", "藏宝图成形", "开启宝藏"],
            "growth": ["认识搭子", "它开始信任你", "交换选择", "形成默契", "写下结局"],
            "comedy": ["麻烦出现", "找回印章", "竹筒去哪了", "临时补救", "终于收拾好"],
        }[style]
        actions = {
            "detective": "记录一个现场细节，并向 NPC 说出你的推理",
            "rescue": "寻找线索但保持距离，不追逐、不投喂、不敲玻璃",
            "archive": "收集这一站的记忆，把它放回旧地图对应的位置",
            "treasure": "完成 NPC 互动，领取这一站的森林印记",
            "growth": "做出一个相处选择，让搭子记住今天的方式",
            "comedy": "完成补救任务，把错位的线索重新排好",
        }[style]
        chapters=[]
        for i, point in enumerate(points):
            clue = clues[i] if i < len(clues) else "一处不打扰动物的观察细节"
            progress = "你已经完成了前面的 NPC 互动。" if i and npc else "这条线索还没有被任何人替你解释。"
            next_point=points[i+1] if i+1<len(points) else "出口"
            choices=[{"id":"investigate", "label":"继续追查这条线索", "effect":"你更相信现场证据，下一站会出现一条可验证的细节。"},{"id":"respect", "label":"先尊重搭子的判断", "effect":"搭子更信任你，下一站会透露一段被隐藏的动机。"}]
            scene=f"{companion} 在{point}停下来，把注意力引向一处容易被忽略的细节。这里是路线中“{route_theme}”的一段。{progress}你收集到的线索是：{clue}。它没有把答案直接交给你，而是把你引向下一站：{next_point}。"
            chapter_label = labels[i] if i < len(labels) else f"第{i + 1}个线索节点"
            chapters.append({"point": point, "label": chapter_label, "scene": scene, "text": scene, "clue": clue, "npc_task": actions, "choices": choices, "next_hint": f"把你的判断带到{next_point}", "action": actions})
        title_suffix = "熊猫与灵长的关系" if "熊猫" in route_theme and "灵长" in route_theme else "本土生境的回声" if "本土" in route_theme else "一条会改变方向的路线"
        return {"title": f"{title_suffix}：{companion}的{STYLE_LABELS[style]}", "subtitle": f"{companion} × {STYLE_LABELS[style]} · {route_theme}", "hook": f"这不是一条可以随便替换节点的路线：你要从{points[0]}出发，经过{points[1]}，最后理解{points[-1]}。{companion}把第一条线索放在入口，因为只有走过中间的每一站，才能看懂“{route_theme}”。", "core_mystery": f"{companion}为什么要把线索拆散在这条路线的节点之间？", "chapters": chapters, "ending": f"你没有把红山变成一场被安排好的表演，而是和{companion}沿着“{route_theme}”走完了这条路线。真正的答案，留在了每个节点之间的关系里。", "possible_endings": ["你选择相信现场证据，找到了线索的表层答案。", "你选择相信搭子，理解了它为什么一直保留这段秘密。"], "modeLabel": STYLE_LABELS[style]}

from __future__ import annotations

import base64
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .agent_service import CompanionAgent
from .bailian_client import BailianClient
from .orchestrator import Orchestrator
from .park_data import park_snapshot, park_topology
from .profile_store import get_companion, save_companion
from .schemas import Preferences, RoutePlanRequest, ReplanRequest, StartSessionRequest, SessionEventRequest
from .session_store import get

app = FastAPI(title="Hongshan Companion API", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
orchestrator = Orchestrator()
companion_agent = CompanionAgent()


class AskRequest(BaseModel):
    question: str
    context: str = ""
    language: str = "zh-CN"
    companion: str = "小红"


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    voice: str | None = None
    model: str | None = None
    language: str = "zh-CN"


class TranscribeRequest(BaseModel):
    audio_url: str
    language: str = "zh-CN"
    model: str | None = None


class StoryRequest(BaseModel):
    companion: str = "小红"
    current_poi: str = "湿地生态区"
    clue: str = "一片没有被风吹走的叶子"
    route: list[dict] = []
    collected_clues: list[str] = []
    completed_npcs: list[str] = []
    style: str = "森林侦探"
    persona: dict = {}


class CompanionSelectionRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    companion: str = Field(min_length=1, max_length=32)
    source: str = Field(default="manual", max_length=32)


@app.get("/health")
def health():
    enabled = BailianClient().enabled
    return {"ok": True, "service": "hongshan-companion", "mode": "bailian" if enabled else "fallback", "bailian_enabled": enabled}


@app.get("/api/park/status")
def park_status():
    return park_snapshot()

@app.get("/api/park/topology")
def topology():
    return park_topology()


@app.put("/api/profile/companion")
def remember_companion(req: CompanionSelectionRequest):
    return save_companion(req.user_id, req.companion, req.source)


@app.get("/api/profile/{user_id}/companion")
def remembered_companion(user_id: str):
    result = get_companion(user_id)
    if not result:
        raise HTTPException(404, "companion choice not found")
    return result


@app.post("/api/route/plan")
def plan(req: RoutePlanRequest):
    return orchestrator.plan(req.natural_language, req.preferences)


@app.post("/api/route/replan")
def replan(req: ReplanRequest):
    result = orchestrator.replan(req.session_id, req.reason, req.keep_pois)
    if not result:
        raise HTTPException(404, "session not found")
    return result


@app.post("/api/session/start")
def start(req: StartSessionRequest):
    # Bootstrap a real route so the session has a start location and a plan to
    # adjust; an empty ordered_pois left every session unusable (IndexError).
    planned = orchestrator.plan("", Preferences())
    route = {
        "route_id": req.route_id or planned["route"]["route_id"],
        "ordered_pois": planned["route"]["ordered_pois"],
        "summary": planned["route"]["summary"],
    }
    return orchestrator.start(route)


@app.post("/api/session/event")
def event(req: SessionEventRequest):
    result = orchestrator.event(req.session_id, req.event_type, req.value, req.note)
    if not result:
        raise HTTPException(404, "session not found")
    return result


@app.get("/api/session/{session_id}")
def session(session_id: str):
    result = get(session_id)
    if not result:
        raise HTTPException(404, "session not found")
    return result


@app.post("/api/assistant/ask")
def ask(req: AskRequest):
    answer, source = companion_agent.answer(req.question, req.context, req.companion, req.language)
    return {"answer": answer, "source": source}


@app.post("/api/story/generate")
def story(req: StoryRequest):
    result, source = companion_agent.story(req.model_dump())
    return {"story": result, "source": source}


@app.post("/api/voice/synthesize")
def synthesize(req: SpeechRequest):
    client = BailianClient()
    if not client.enabled:
        return {"enabled": False, "audio_base64": None, "message": "请在 backend/.env 配置 DASHSCOPE_API_KEY"}
    try:
        from dashscope.audio.tts_v2 import SpeechSynthesizer
        synthesizer = SpeechSynthesizer(
            model=req.model or os.getenv("COSYVOICE_MODEL", "cosyvoice-v1"),
            voice=req.voice or os.getenv("COSYVOICE_VOICE", "longxiaochun"),
        )
        # dashscope 1.26 defaults to async mode, which returns None before
        # the audio buffer is complete. We need the completed bytes for HTTP.
        synthesizer.async_call = False
        audio = synthesizer.call(req.text)
        if not audio:
            detail = getattr(synthesizer, "last_response", None)
            raise RuntimeError(f"CosyVoice returned empty audio: text={req.text!r}, response={detail}")
        return {"enabled": True, "mime_type": "audio/mpeg", "audio_base64": base64.b64encode(audio).decode("ascii")}
    except Exception as exc:
        return {"enabled": False, "audio_base64": None, "message": f"语音服务暂不可用：{exc}"}
@app.post("/api/voice/transcribe")
def transcribe(req: TranscribeRequest):
    """Transcribe one temporary audio URL with Bailian Paraformer."""
    client = BailianClient()
    if not client.enabled:
        return {"enabled": False, "text": "", "message": "请在 backend/.env 配置 DASHSCOPE_API_KEY"}
    try:
        import dashscope
        import httpx
        dashscope.api_key = client.api_key
        model = req.model or os.getenv("ASR_MODEL", "paraformer-v2")
        task = dashscope.audio.asr.Transcription.async_call(model=model, file_urls=[req.audio_url])
        task_id = getattr(getattr(task, "output", None), "task_id", None)
        if not task_id:
            raise RuntimeError("ASR task id was not returned")
        result = dashscope.audio.asr.Transcription.wait(task=task_id)
        results = getattr(getattr(result, "output", None), "results", None) or []
        texts: list[str] = []
        for item in results:
            url = item.get("transcription_url") if isinstance(item, dict) else getattr(item, "transcription_url", None)
            if url:
                payload = httpx.get(url, timeout=30).json()
                texts.append(str(payload.get("transcripts", [{}])[0].get("text", "")))
        return {"enabled": True, "text": " ".join(x for x in texts if x).strip(), "language": req.language, "model": model}
    except Exception as exc:
        return {"enabled": False, "text": "", "message": f"语音识别暂不可用：{exc}"}

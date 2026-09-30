"""Alibaba Cloud Bailian / DashScope client.

The API key is intentionally read only from environment variables.  Never put
it in the frontend bundle or commit it to source control.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class BailianClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("BAILIAN_API_KEY")
        self.base_url = os.getenv(
            "DASHSCOPE_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ).rstrip("/")
        self.model = os.getenv("QWEN_MODEL", "qwen-plus")
        self.enabled = bool(self.api_key) and _env_bool("ENABLE_BAILIAN", True)

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str | None:
        if not self.enabled:
            return None
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "enable_thinking": False,
            },
            timeout=float(os.getenv("BAILIAN_TIMEOUT_SECONDS", "30")),
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content")

    @staticmethod
    def parse_json(content: str | None) -> dict[str, Any] | None:
        if not content:
            return None
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        # Qwen 偶发输出 Python 风格的 True/False/None，归一化为合法 JSON 字面量
        text = re.sub(r"\bTrue\b", "true", text)
        text = re.sub(r"\bFalse\b", "false", text)
        text = re.sub(r"\bNone\b", "null", text)
        try:
            value = json.loads(text)
            return value if isinstance(value, dict) else None
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            if start >= 0 and end > start:
                try:
                    value = json.loads(text[start : end + 1])
                    return value if isinstance(value, dict) else None
                except json.JSONDecodeError:
                    return None

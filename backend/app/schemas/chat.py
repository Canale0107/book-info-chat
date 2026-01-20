from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class DebugLogEntry(BaseModel):
    timestamp: str
    type: Literal["openai_request", "openai_response", "tool_call", "tool_result", "cinii_request", "cinii_response", "error"]
    summary: str
    details: Optional[dict] = None


class ChatResponse(BaseModel):
    message: str
    books: Optional[list[dict]] = None  # 検索結果がある場合
    debug_logs: Optional[list[DebugLogEntry]] = None  # デバッグログ

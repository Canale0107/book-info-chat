import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import process_chat, process_chat_stream

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    チャットメッセージを処理する

    ユーザーのメッセージと会話履歴を受け取り、
    必要に応じて本を検索して推薦文を返す。
    """
    return await process_chat(
        message=request.message,
        history=request.history,
    )


@router.post("/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    チャットメッセージをストリーミングで処理する（SSE）

    各処理ステップをリアルタイムでクライアントに送信する。
    """
    async def event_generator():
        async for event in process_chat_stream(
            message=request.message,
            history=request.history,
        ):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import process_chat

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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import books, chat

app = FastAPI(
    title="Book Info Chat API",
    description="自然言語で本を検索・推薦するチャットボットのバックエンドAPI",
    version="0.1.0",
)

# CORS設定（Next.jsフロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(books.router)
app.include_router(chat.router)


@app.get("/health")
async def health_check():
    """ヘルスチェック用エンドポイント"""
    return {"status": "ok"}

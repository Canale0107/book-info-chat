from fastapi import APIRouter, HTTPException
from app.schemas.book import BookSearchParams, BookSearchResponse
from app.services.cinii import search_books, CiNiiAPIError

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/search", response_model=BookSearchResponse)
async def search_books_endpoint(params: BookSearchParams) -> BookSearchResponse:
    """
    書籍を検索する（CiNii Books API経由）

    LLMのtool callingから呼び出されることを想定。
    エラーはLLM向けに分類して返す。
    """
    try:
        return await search_books(params)
    except CiNiiAPIError as e:
        # LLM向けのエラーレスポンス（再試行可能かどうかを判断できるように）
        status_code = {
            "invalid_input": 400,
            "config_error": 500,
            "timeout": 504,
            "rate_limit": 429,
            "api_error": 502,
            "connection_error": 503,
        }.get(e.error_type, 500)

        raise HTTPException(
            status_code=status_code,
            detail={
                "error_type": e.error_type,
                "message": e.message,
                "retryable": e.error_type in ["timeout", "rate_limit", "connection_error"],
            }
        )

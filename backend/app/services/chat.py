import json
from datetime import datetime
from typing import AsyncGenerator
from openai import AsyncOpenAI, AuthenticationError, APIError
from app.config import get_settings
from app.schemas.chat import ChatMessage, ChatResponse, DebugLogEntry
from app.schemas.book import BookSearchParams
from app.services.cinii import search_books, CiNiiAPIError


def create_log(
    log_type: str,
    summary: str,
    details: dict | None = None
) -> DebugLogEntry:
    """デバッグログエントリを作成"""
    return DebugLogEntry(
        timestamp=datetime.now().isoformat(),
        type=log_type,
        summary=summary,
        details=details,
    )


# Tool定義（search_books）
SEARCH_BOOKS_TOOL = {
    "type": "function",
    "function": {
        "name": "search_books",
        "description": "CiNii Books APIを使って本を検索する。ユーザーの要望に応じて適切な検索条件を設定する。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "フリーワード検索（タイトル、著者、キーワードなど何でも）"
                },
                "title": {
                    "type": "string",
                    "description": "タイトルで絞り込む場合"
                },
                "author": {
                    "type": "string",
                    "description": "著者名で絞り込む場合"
                },
                "publisher": {
                    "type": "string",
                    "description": "出版社で絞り込む場合"
                },
                "year_from": {
                    "type": "integer",
                    "description": "出版年の下限（例: 2020）"
                },
                "year_to": {
                    "type": "integer",
                    "description": "出版年の上限（例: 2024）"
                },
                "count": {
                    "type": "integer",
                    "description": "取得件数（デフォルト10、最大20）",
                    "default": 10
                }
            },
            "required": []
        }
    }
}

SYSTEM_PROMPT = """あなたは本を推薦するチャットボットです。

ユーザーの興味、気分、悩み、テーマなどを聞き取り、適切な本を推薦してください。

## 基本的な流れ
1. ユーザーの話を聞いて、何を求めているか理解する
2. 必要に応じて search_books ツールを使って本を検索する
3. 検索結果から3冊程度を選び、なぜおすすめするかの理由を添えて紹介する
4. ユーザーの反応を見て、さらに絞り込んだり別の方向性を提案したりする

## 推薦のコツ
- 所蔵館数（owner_count）が多い本は広く読まれている証拠
- ユーザーが「軽め」と言えば入門書や新書を、「深い」と言えば専門書を探す
- 雑談から興味を引き出し、検索キーワードを工夫する

## 注意点
- 検索結果がない場合は、別のキーワードで再検索を提案する
- 本の情報は正確に伝える（タイトル、著者、出版年など）
- Amazonリンクは提供しない（将来対応予定）
"""


async def process_chat_stream(
    message: str,
    history: list[ChatMessage],
) -> AsyncGenerator[dict, None]:
    """チャットメッセージを処理し、各ステップをストリーミングで返す"""
    settings = get_settings()

    if not settings.openai_api_key:
        yield {"type": "error", "data": {"message": "OpenAI APIキーが設定されていません。"}}
        return

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # メッセージ履歴を構築
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": message})

    # ログ: OpenAIリクエスト
    yield {"type": "log", "data": create_log(
        "openai_request",
        "Backend → OpenAI: チャット補完リクエスト",
        {"model": "gpt-4o-mini", "tools": ["search_books"], "message_count": len(messages)}
    ).model_dump()}

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=[SEARCH_BOOKS_TOOL],
            tool_choice="auto",
        )
    except AuthenticationError:
        yield {"type": "log", "data": create_log("error", "OpenAI API 認証エラー").model_dump()}
        yield {"type": "error", "data": {"message": "OpenAI APIキーが無効です。"}}
        return
    except APIError as e:
        yield {"type": "log", "data": create_log("error", f"OpenAI API エラー: {e.message}").model_dump()}
        yield {"type": "error", "data": {"message": f"OpenAI APIでエラーが発生しました: {e.message}"}}
        return

    assistant_message = response.choices[0].message
    found_books = None

    # ログ: OpenAIレスポンス
    has_tool_calls = bool(assistant_message.tool_calls)
    yield {"type": "log", "data": create_log(
        "openai_response",
        f"OpenAI → Backend: レスポンス (tool_call: {'あり' if has_tool_calls else 'なし'})",
        {"has_tool_calls": has_tool_calls, "finish_reason": response.choices[0].finish_reason}
    ).model_dump()}

    # Tool callがある場合は実行
    if assistant_message.tool_calls:
        tool_results = []

        for tool_call in assistant_message.tool_calls:
            if tool_call.function.name == "search_books":
                args = json.loads(tool_call.function.arguments)

                # ログ: Tool call検出
                yield {"type": "log", "data": create_log(
                    "tool_call",
                    "OpenAI が search_books の実行を要求",
                    {"arguments": args}
                ).model_dump()}

                # count上限を設定
                if args.get("count", 10) > 20:
                    args["count"] = 20

                # ログ: CiNiiリクエスト
                yield {"type": "log", "data": create_log(
                    "cinii_request",
                    "Backend → CiNii: 書籍検索リクエスト",
                    {"params": args}
                ).model_dump()}

                try:
                    params = BookSearchParams(**args)
                    result = await search_books(params)
                    found_books = [book.model_dump() for book in result.books]

                    # ログ: CiNiiレスポンス
                    yield {"type": "log", "data": create_log(
                        "cinii_response",
                        f"CiNii → Backend: {result.total}件中{len(result.books)}件取得",
                        {"total": result.total, "returned": len(result.books)}
                    ).model_dump()}

                    tool_result = json.dumps({
                        "total": result.total,
                        "books": found_books,
                    }, ensure_ascii=False)
                except CiNiiAPIError as e:
                    yield {"type": "log", "data": create_log(
                        "error",
                        f"CiNii API エラー: {e.message}",
                        {"error_type": e.error_type}
                    ).model_dump()}
                    tool_result = json.dumps({
                        "error": e.message,
                        "error_type": e.error_type,
                    }, ensure_ascii=False)

                # ログ: Tool結果
                yield {"type": "log", "data": create_log(
                    "tool_result",
                    "Backend → OpenAI: 検索結果を送信",
                    {"tool_call_id": tool_call.id}
                ).model_dump()}

                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": tool_result,
                })

        # Tool結果を含めて再度API呼び出し
        messages.append(assistant_message.model_dump())
        messages.extend(tool_results)

        # ログ: 2回目のOpenAIリクエスト
        yield {"type": "log", "data": create_log(
            "openai_request",
            "Backend → OpenAI: 検索結果を含めて最終リクエスト",
            {"model": "gpt-4o-mini", "message_count": len(messages)}
        ).model_dump()}

        try:
            final_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            final_message = final_response.choices[0].message.content

            # ログ: 最終レスポンス
            yield {"type": "log", "data": create_log(
                "openai_response",
                "OpenAI → Backend: 最終回答を受信",
                {"finish_reason": final_response.choices[0].finish_reason}
            ).model_dump()}
        except APIError as e:
            yield {"type": "log", "data": create_log("error", f"OpenAI API エラー: {e.message}").model_dump()}
            yield {"type": "error", "data": {"message": f"OpenAI APIでエラーが発生しました: {e.message}"}}
            return
    else:
        final_message = assistant_message.content

    # 最終結果を送信
    yield {"type": "done", "data": {
        "message": final_message or "",
        "books": found_books,
    }}


# 従来の非ストリーミング版も残す（互換性のため）
async def process_chat(
    message: str,
    history: list[ChatMessage],
) -> ChatResponse:
    """チャットメッセージを処理し、必要に応じて本を検索して推薦する"""
    debug_logs = []
    result_message = ""
    result_books = None

    async for event in process_chat_stream(message, history):
        if event["type"] == "log":
            debug_logs.append(DebugLogEntry(**event["data"]))
        elif event["type"] == "done":
            result_message = event["data"]["message"]
            result_books = event["data"]["books"]
        elif event["type"] == "error":
            result_message = event["data"]["message"]

    return ChatResponse(
        message=result_message,
        books=result_books,
        debug_logs=debug_logs,
    )

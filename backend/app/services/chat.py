import json
from openai import AsyncOpenAI, AuthenticationError, APIError
from app.config import get_settings
from app.schemas.chat import ChatMessage, ChatResponse
from app.schemas.book import BookSearchParams
from app.services.cinii import search_books, CiNiiAPIError

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


async def process_chat(
    message: str,
    history: list[ChatMessage],
) -> ChatResponse:
    """チャットメッセージを処理し、必要に応じて本を検索して推薦する"""
    settings = get_settings()

    if not settings.openai_api_key:
        return ChatResponse(
            message="OpenAI APIキーが設定されていません。管理者に連絡してください。"
        )

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # メッセージ履歴を構築
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": message})

    try:
        # OpenAI API呼び出し（tool calling有効）
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=[SEARCH_BOOKS_TOOL],
            tool_choice="auto",
        )
    except AuthenticationError:
        return ChatResponse(
            message="OpenAI APIキーが無効です。正しいAPIキーを設定してください。"
        )
    except APIError as e:
        return ChatResponse(
            message=f"OpenAI APIでエラーが発生しました: {e.message}"
        )

    assistant_message = response.choices[0].message
    found_books = None

    # Tool callがある場合は実行
    if assistant_message.tool_calls:
        tool_results = []

        for tool_call in assistant_message.tool_calls:
            if tool_call.function.name == "search_books":
                args = json.loads(tool_call.function.arguments)

                # count上限を設定
                if args.get("count", 10) > 20:
                    args["count"] = 20

                try:
                    params = BookSearchParams(**args)
                    result = await search_books(params)
                    found_books = [book.model_dump() for book in result.books]
                    tool_result = json.dumps({
                        "total": result.total,
                        "books": found_books,
                    }, ensure_ascii=False)
                except CiNiiAPIError as e:
                    tool_result = json.dumps({
                        "error": e.message,
                        "error_type": e.error_type,
                    }, ensure_ascii=False)

                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": tool_result,
                })

        # Tool結果を含めて再度API呼び出し
        messages.append(assistant_message.model_dump())
        messages.extend(tool_results)

        try:
            final_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
            final_message = final_response.choices[0].message.content
        except APIError as e:
            return ChatResponse(
                message=f"OpenAI APIでエラーが発生しました: {e.message}",
                books=found_books,
            )
    else:
        final_message = assistant_message.content

    return ChatResponse(
        message=final_message or "",
        books=found_books,
    )

import httpx
from typing import Optional
from app.schemas.book import Book, BookSearchParams, BookSearchResponse
from app.config import get_settings

CINII_BOOKS_API_URL = "https://ci.nii.ac.jp/books/opensearch/search"


class CiNiiAPIError(Exception):
    """CiNii API関連のエラー"""
    def __init__(self, message: str, error_type: str = "api_error"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


async def search_books(params: BookSearchParams) -> BookSearchResponse:
    """CiNii Books APIで書籍を検索する"""
    settings = get_settings()

    if not settings.cinii_app_id:
        raise CiNiiAPIError("CiNii APP ID is not configured", "config_error")

    query_params = {
        "format": "json",
        "appid": settings.cinii_app_id,
        "count": params.count,
    }

    if params.query:
        query_params["q"] = params.query
    if params.title:
        query_params["title"] = params.title
    if params.author:
        query_params["author"] = params.author
    if params.publisher:
        query_params["publisher"] = params.publisher
    if params.year_from:
        query_params["year_from"] = params.year_from
    if params.year_to:
        query_params["year_to"] = params.year_to

    # クエリが空の場合はエラー
    search_fields = [params.query, params.title, params.author, params.publisher]
    if not any(search_fields):
        raise CiNiiAPIError(
            "At least one search parameter (query, title, author, publisher) is required",
            "invalid_input"
        )

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(CINII_BOOKS_API_URL, params=query_params)
            response.raise_for_status()
        except httpx.TimeoutException:
            raise CiNiiAPIError("CiNii API request timed out", "timeout")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise CiNiiAPIError("Rate limit exceeded", "rate_limit")
            raise CiNiiAPIError(f"CiNii API returned error: {e.response.status_code}", "api_error")
        except httpx.RequestError as e:
            raise CiNiiAPIError(f"Failed to connect to CiNii API: {str(e)}", "connection_error")

    data = response.json()
    books = _parse_cinii_response(data)

    # 使用したクエリ情報（デバッグ/透明性用）
    query_used = {k: v for k, v in query_params.items() if k not in ["format", "appid"]}

    return BookSearchResponse(
        total=data.get("@graph", [{}])[0].get("opensearch:totalResults", 0) if data.get("@graph") else 0,
        books=books,
        query_used=query_used,
    )


def _parse_cinii_response(data: dict) -> list[Book]:
    """CiNii JSON-LDレスポンスをBook型に変換する"""
    books = []

    graph = data.get("@graph", [])
    if not graph:
        return books

    # @graph[0].items に書籍データが入っている
    channel = graph[0] if graph else {}
    items = channel.get("items", [])

    for item in items:
        # タイトル取得（"title" または "dc:title"）
        title = item.get("title") or _get_value(item, "dc:title")
        if not title:
            continue

        # 著者取得
        creators = item.get("dc:creator", [])
        if isinstance(creators, str):
            creators = [creators]
        elif isinstance(creators, list):
            creators = [_get_value(c) if isinstance(c, dict) else c for c in creators]
        else:
            creators = []

        # 出版社取得
        publishers = item.get("dc:publisher", [])
        if isinstance(publishers, list):
            publisher = publishers[0] if publishers else None
        else:
            publisher = publishers

        # 出版年取得
        year = item.get("prism:publicationDate") or item.get("dc:date")

        # ISBN取得
        isbn = None
        identifiers = item.get("dcterms:hasPart", [])
        if isinstance(identifiers, dict):
            identifiers = [identifiers]
        for ident in identifiers:
            ident_value = ident.get("@id", "")
            if "urn:isbn:" in ident_value.lower():
                isbn = ident_value.replace("urn:isbn:", "").replace("URN:ISBN:", "")
                break

        # 所蔵館数（文字列で返ってくるのでintに変換）
        owner_count_raw = item.get("cinii:ownerCount")
        owner_count = int(owner_count_raw) if owner_count_raw else None

        # CiNii URL
        cinii_url = item.get("@id", "")

        # ID抽出
        book_id = cinii_url.split("/")[-1] if cinii_url else ""

        books.append(Book(
            id=book_id,
            title=title,
            authors=creators,
            publisher=publisher,
            year=year,
            isbn=isbn,
            owner_count=owner_count,
            cinii_url=cinii_url,
        ))

    return books


def _get_value(item: dict, key: str) -> Optional[str]:
    """JSON-LDの値を取得（@valueがある場合はその値を返す）"""
    value = item.get(key)
    if isinstance(value, dict):
        return value.get("@value")
    return value

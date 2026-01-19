from pydantic import BaseModel
from typing import Optional


class BookSearchParams(BaseModel):
    """検索パラメータ（LLMのtool callingから渡される）"""
    query: Optional[str] = None  # フリーワード検索
    title: Optional[str] = None  # タイトル
    author: Optional[str] = None  # 著者
    publisher: Optional[str] = None  # 出版社
    year_from: Optional[int] = None  # 出版年（から）
    year_to: Optional[int] = None  # 出版年（まで）
    count: int = 10  # 取得件数


class Book(BaseModel):
    """書誌情報（LLMに渡す最小限の情報）"""
    id: str  # CiNii ID
    title: str
    authors: list[str]
    publisher: Optional[str] = None
    year: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    owner_count: Optional[int] = None  # 所蔵館数
    cinii_url: str


class BookSearchResponse(BaseModel):
    """検索結果レスポンス"""
    total: int
    books: list[Book]
    query_used: dict  # 実際に使用したクエリ（デバッグ用）

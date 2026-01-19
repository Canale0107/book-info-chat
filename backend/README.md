# Book Info Chat Backend

自然言語で本を検索・推薦するチャットボットのバックエンドAPI

## 技術スタック

- Python 3.12+
- FastAPI
- OpenAI API (GPT-4o)
- CiNii Books API
- uv (パッケージマネージャー)

## セットアップ

### 1. 依存関係のインストール

```bash
uv sync
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` ファイルを編集して、以下のAPIキーを設定してください：

| 変数名 | 説明 |
|--------|------|
| `CINII_APP_ID` | CiNii APIのアプリケーションID ([CiNii](https://support.nii.ac.jp/ja/cinii/api/developer)で取得) |
| `OPENAI_API_KEY` | OpenAI APIキー |
| `HOST` | サーバーホスト (デフォルト: `0.0.0.0`) |
| `PORT` | サーバーポート (デフォルト: `8000`) |

### 3. サーバーの起動

```bash
uv run uvicorn app.main:app --reload
```

## APIエンドポイント

### `GET /health`
ヘルスチェック用

### `POST /chat`
チャットメッセージを処理し、本の推薦を返す

**リクエスト:**
```json
{
  "message": "プログラミングの入門書を探しています",
  "history": []
}
```

**レスポンス:**
```json
{
  "message": "プログラミングの入門書をお探しですね。以下の本をおすすめします...",
  "books": [
    {
      "id": "...",
      "title": "...",
      "authors": ["..."],
      "publisher": "...",
      "year": "2024",
      "cinii_url": "https://...",
      "owner_count": 100
    }
  ]
}
```

### `POST /books/search`
CiNii Books APIを使用して書籍を検索（内部利用）

## ディレクトリ構成

```
backend/
├── app/
│   ├── main.py          # FastAPIアプリケーション
│   ├── config.py        # 設定（環境変数）
│   ├── routers/
│   │   ├── chat.py      # チャットエンドポイント
│   │   └── books.py     # 書籍検索エンドポイント
│   ├── schemas/
│   │   ├── chat.py      # チャット関連のスキーマ
│   │   └── book.py      # 書籍関連のスキーマ
│   └── services/
│       ├── chat.py      # チャット処理ロジック
│       └── cinii.py     # CiNii API連携
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## API ドキュメント

サーバー起動後、以下のURLでSwagger UIを確認できます：

http://localhost:8000/docs

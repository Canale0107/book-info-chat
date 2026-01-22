# Book Info Chat

自然言語で会話しながら本を探せるチャットボット。

LLMがユーザーの意図を理解し、CiNii Books APIを使って本を検索・推薦します。

## Demo

![デモ1](assets/screenshot-1.png)
![デモ2](assets/screenshot-2.png)
![デモ3](assets/screenshot-3.png)

## 技術スタック

- **フロントエンド**: Next.js (TypeScript, Tailwind CSS)
- **バックエンド**: FastAPI (Python)
- **LLM**: OpenAI API (GPT-4o-mini, Tool Calling)
- **書籍検索**: CiNii Books API

## セットアップ

### 必要なもの

- Python 3.11+
- Node.js 18+
- CiNii アプリケーションID
- OpenAI API キー

### APIキーの取得

1. **CiNii アプリケーションID**
   - https://support.nii.ac.jp/ja/cinii/api/developer から申請

2. **OpenAI API キー**
   - https://platform.openai.com/api-keys から取得

### バックエンド

```bash
cd backend

# 環境変数を設定
cp .env.example .env
# .env を編集して CINII_APP_ID と OPENAI_API_KEY を設定

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# 起動
uvicorn app.main:app --reload
```

### フロントエンド

```bash
cd frontend

# 依存関係をインストール
npm install

# 起動
npm run dev
```

## アクセス

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

## API エンドポイント

### POST /chat

チャットメッセージを処理し、本を推薦します。

```json
{
  "message": "プログラミングの入門書を探しています",
  "history": []
}
```

### POST /books/search

CiNii Books APIで書籍を検索します。

```json
{
  "query": "Python",
  "author": "オライリー",
  "count": 10
}
```

## プロジェクト構造

```
book-info-chat/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPIエントリポイント
│   │   ├── config.py        # 環境変数設定
│   │   ├── routers/
│   │   │   ├── books.py     # 書籍検索エンドポイント
│   │   │   └── chat.py      # チャットエンドポイント
│   │   ├── services/
│   │   │   ├── cinii.py     # CiNii API連携
│   │   │   └── chat.py      # OpenAI Tool Calling
│   │   └── schemas/         # Pydanticモデル
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx     # メインチャットUI
│   │   ├── components/
│   │   │   ├── ChatMessage.tsx
│   │   │   └── ChatInput.tsx
│   │   └── lib/
│   │       └── api.ts       # API呼び出し
│   └── .env.local.example
│
└── blueprint.md             # 設計ドキュメント
```

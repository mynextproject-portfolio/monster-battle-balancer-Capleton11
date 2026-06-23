# 🌙 モンスターバトル（仮） — 月夜ゲームス

D&D をテーマにした新作ゲームの出発点となるプロジェクトです。
現在は、2体のモンスターを選んでステータスカードを見比べることができます。

*Tsukiyo Games — starting point for a new D&D-themed game. Currently you can pick two
monsters and compare their stat cards.*

> ⚠️ UI は現在日本語のみです。/ The UI is currently Japanese only.

## セットアップ / Setup

> Python `3.12` または `3.13` を使用してください。/ Use Python 3.12 or 3.13.

```bash
python3.12 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## 実行 / Run

```bash
python main.py
```

## テスト / Test

```bash
pytest
```

## Docker（任意 / optional）

ローカル開発には不要です。Web アプリとして配信したい場合のみ使用します。
*Not needed for local development — only for serving the app over the web.*

```bash
docker build -t monster-battle .
docker run -p 8000:8000 monster-battle      # http://localhost:8000
```

---

*Part of [mynextproject.dev](https://mynextproject.dev) - Learn to code like a professional*

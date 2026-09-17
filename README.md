# AI Operations Copilot

AI x Data Engineering x DX x Power BI x Machine Learning を組み合わせた、意思決定支援のポートフォリオプロジェクトです。

企業データを模したSynthetic DataをPythonで生成・検証し、PostgreSQL、分析、異常検知、売上予測、Power BI、Evidence-first AI Insightへつなげます。実在企業のデータや機密情報は使用しません。

## Project Design

実装前の要件、MVP範囲、データモデル、アーキテクチャ、ロードマップ、Power BI設計は [PROJECT_DESIGN.md](PROJECT_DESIGN.md) にまとめています。

## Current Status

- Synthetic Data: 実装済み。seedを指定した再現可能な店舗、商品、顧客、売上、在庫データ
- ETL: 実装済み。データ品質検証、売上日次集計、在庫リスク特徴量
- Machine Learning: 実装済み。Isolation Forest異常検知、BaselineとRandom Forestの予測比較
- AI Operations Copilot: 実装済み。EvidenceとPossible Factorsを分離するローカルテンプレート
- PostgreSQL: DDLとDocker Composeを実装済み。Docker Desktop起動後に初期化を検証
- Power BI: データモデルと5ページ設計を確定。PBIXは後続Phaseで作成

## Architecture

```text
Synthetic Data
	|
Python Cleaning / Validation / Feature Engineering
	|
PostgreSQL -------- Power BI Desktop
	|
Anomaly Detection / Forecast
	|
Structured Evidence
	|
Local LLM or Evidence-first Template
	|
Business Insight / Recommended Action
```

## Local Setup

Python 3.10以上とDocker Desktopが必要です。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

PostgreSQLを起動する場合は、Docker Desktopを起動してから実行します。

```powershell
Copy-Item .env.example .env
docker compose up -d
```

## Generate Synthetic Data

```powershell
$env:PYTHONPATH = "src"
python scripts/generate_synthetic_data.py
```

生成されるCSVは `data/generated/` に保存されます。このディレクトリはGit管理対象外です。デフォルトではseed `42`、90日間、8店舗、40商品、300顧客を使用します。売上には曜日・季節性・店舗差・割引を、在庫には補充・販売数量・再発注点を反映します。

## Run Tests

```powershell
pytest -q
```

現在の自動テストは、データ生成の再現性、参照整合性、予測モデル比較、AI出力の事実・推測分離を確認します。評価値はテスト実行時に計算した値だけを扱い、未測定の精度をプロジェクト説明に記載しません。

## Technology

- Python, pandas, NumPy
- PostgreSQL 16, Docker Compose
- scikit-learn
- Power BI Desktop, Power Query, DAX
- Git, GitHub

初期のAI生成は有料APIを必須にせず、構造化結果をローカルLLMまたはテンプレートへ渡す設計です。

## Next Steps

1. Docker起動後にPostgreSQLのDDL適用を確認する
2. CSV/分析結果をPostgreSQLへロードするETLを追加する
3. Power BI DesktopでExecutive Overviewから順に作成する
4. ローカルLLM利用時のプロンプト、出力検証、スクリーンショットを追加する
5. 実測した評価結果と制約をREADMEへ追記する
# 就職活動向けプロジェクト紹介

## プロジェクト名

**AI Operations Copilot**

## 30秒説明

企業業務を想定したSynthetic DataをPythonで生成・検証し、PostgreSQLに統合します。そのデータを使って、Power BIでKPIを可視化し、Pythonとscikit-learnで異常検知・売上予測を行います。最後に、分析済みのEvidenceだけをローカルAIへ渡し、事実と推測を分けた業務改善アクションを提示する意思決定支援システムです。

## 履歴書・職務経歴書向けの記載例

### 日本語

- Python、pandas、NumPy、PostgreSQL、Power BI、scikit-learnを組み合わせた業務データ分析基盤を設計・実装
- 再現可能なSynthetic Data生成、データ品質検証、ETL、KPI集計、異常検知、売上予測を一連のパイプラインとして構築
- Isolation ForestとBaselineを比較し、MAE/RMSEを実測してモデル評価を記録
- Power BIのDAX Measures、テーブルリレーション、カレンダーテーブルを設計
- AIには生データ全体を渡さず、Pythonで抽出したEvidenceを渡すことで、事実と推測を分離したInsightを生成
- Docker Compose、pytest、GitHubによってローカル再現性と変更履歴を管理

### 技術キーワード

`Python` `pandas` `NumPy` `PostgreSQL` `Docker` `Power BI` `DAX` `Power Query` `scikit-learn` `Isolation Forest` `Forecasting` `Data Quality` `ETL` `GitHub`

## 面接で説明するポイント

1. **なぜSynthetic Dataか**: 実在企業の機密情報を使わず、生成条件とseedを明示して再現性を確保するためです。
2. **なぜPower BIか**: 分析結果を経営・店舗・商品担当者が比較し、フィルターやドリルダウンで確認できる形にするためです。
3. **AIの安全性**: AIにデータベース全体を渡さず、検証済みの構造化Evidenceだけを入力します。原因を確認できない場合は推測として表示します。
4. **モデル評価**: 実測していない精度を記載せず、同じ評価期間でBaselineとML ModelのMAE/RMSEを比較します。
5. **今後の改善**: PostgreSQL接続、Power BIの5ページ完成、ローカルLLM接続、データ品質レポート、予測の継続評価を追加します。

## Power BIスクリーンショットの保存

Power BI Desktopでページを表示し、`Win + Shift + S`でレポート部分だけを切り取ります。PNG形式で次の名前にしてください。

```text
docs/screenshots/01-executive-overview.png
docs/screenshots/02-store-analysis.png
docs/screenshots/03-product-analysis.png
docs/screenshots/04-forecast-risk.png
docs/screenshots/05-ai-insights.png
```

スクリーンショットには、ページ名、KPI、フィルター、グラフのタイトルが見えるようにします。個人情報や実在企業名は入れません。画像を追加したら、READMEのPower BI Screenshots欄からリンクします。

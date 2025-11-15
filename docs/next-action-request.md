# Next Action Request – YouTube Dashboard Frontend

## 1. 現在の状態（2025-11-15）
- `feature/update-dashboard` ブランチを作成し、以降の作業はこのブランチで進行中。
- プロジェクト共通メモ (`NOTES.md`) を整備。作業ログと共有済みのネクストアクションを常時更新。
- フロントエンド仕様書 `docs/plan.md` を作成。Next.js 14 + Tailwind + TanStack Query + Recharts を前提に、画面仕様・API コントラクト・DoD・CodeX タスク手順を網羅。
- バックエンド仕様書 `docs/zawa-backend-spec.md` を作成。Lambda/RDS/DynamoDB/YouTube Data API/Streamlit の役割と API 擬似コード、環境変数まで記載。
- CodeX へ渡すためのドキュメントを追加：
  - `docs/codex-system-prompt.md` … CodeX 向けシステムプロンプト（責務・禁止事項・出力形式・優先度など）。
  - `docs/codex-task-template.md` … 個別タスク依頼用テンプレ（例として `/channels/import` 実装タスクを記載）。

## 2. 依頼したいネクストアクション
1. **仕様確認フィードバック**
   - `docs/plan.md`・`docs/zawa-backend-spec.md`・`docs/codex-system-prompt.md` の内容に齟齬や不足がないか確認し、追記・修正が必要なら指示してください。
2. **CodeX 起動の Go サイン**
   - CodeX に作業を依頼して良いか（特に `.env.local`/`lib/api.ts` 整備 → `/channels/import` 実装から着手で問題ないか）判断をお願いします。
3. **バックエンド着手の優先度**
   - ざわ側で RDS スキーマ・Lambda 実装を進めてよいか、優先順位と担当範囲を明確化してもらえると助かります。
4. **追加で必要なドキュメントやタスク整理**
   - Streamlit 側詳細仕様や GitHub Projects/Issue テンプレートなど、必要な補足資料があれば依頼内容を教えてください。

## 3. 補足
- 現在の最優先フロントタスクは `NOTES.md` の「共有済みフロント側ネクストアクション」に列挙済みです。
- CodeX 用ドキュメントは `docs/` 配下に揃えているので、レビュー後すぐ実行に移せます。

以上、ご確認のうえ次のアクション指示をいただければ、その内容に沿って進めます。

# YouTube Dashboard 作業メモ

## 実施内容

### 2025-11-15
- GitHub から `nynynakazawa/youtube-dashboard` をクローンし、作業用ブランチ `feature/update-dashboard` を作成。
- 連絡用の `NOTES.md` を用意し、以降のタスクログ置き場として運用開始。
- フロントエンド実装を codeX へ委譲できるよう、`docs/plan.md` に Next.js/Tailwind/TanStack Query/Recharts/React Query などの技術選定、API 仕様、画面要件、DoD、タスクプロンプトを詳細に記述。
- バックエンド担当（ざわ）向けに、Lambda・RDS・DynamoDB・YouTube Data API・Streamlit の責務とディレクトリ構成、環境変数、進め方をまとめた `docs/zawa-backend-spec.md` を作成。
- 上記ドキュメントはすべて `feature/update-dashboard` ブランチでコミット・プッシュ済み。フロント/バック双方が `docs/` 配下の md を参照すればすぐ着手できる状態。

## 共有事項・Next Action 依頼
- `docs/plan.md`（フロント計画）と `docs/zawa-backend-spec.md`（バックエンド計画）の内容確認をお願いします。仕様に追加・修正が必要であればコメントが欲しいです。
- codeX へフロント実装を投げる場合は、docs/plan.md のマスタープロンプトとタスクプロンプトの手順で進めてもらえるか確認したいです。
- バックエンド側で RDS スキーマ定義や Lambda 実装に着手してよいか、優先順位や担当分担について指示をください。
- 他に必要なドキュメント（例: Streamlit 側の仕様、GitHub Projects でのタスク整理など）があればリクエストをお願いします。

## 共有済みフロント側ネクストアクション（優先順）
1. **API 基盤整備**  
   - `.env.local` に `NEXT_PUBLIC_API_BASE_URL=https://{api-id}.execute-api.{region}.amazonaws.com/prod` を追加し、`lib/api.ts` を先行作成して API 呼び出しの入口を統一する。  
   - `importChannel` / `getChannels` / `getChannelVideos` などはこのモジュール経由で提供し、バックエンド完成前でもモック差し替えを容易にする。
2. **チャンネル登録フォーム（/channels/import）**  
   - `app/(routes)/channels/import/page.tsx` を作成し、チャンネル URL/ID 入力、送信ボタン、ローディング表示、エラー表示を実装。  
   - `lib/api.ts` の `importChannel` を呼び、成功時は同ページ内にチャンネル情報＋サマリカードを表示（後で詳細ページ遷移に拡張予定）。
3. **チャンネル一覧ページ（/channels）**  
   - `app/(routes)/channels/page.tsx` を用意し、`getChannels`（当面はモック）で取得したデータをカード/テーブル表示。  
   - 行クリックで `/channels/[id]/videos` へ遷移できるようにし、UX の導線を固定する。
4. **動画一覧ページの土台（/channels/[id]/videos）**  
   - URL 構造だけでも決めて `app/(routes)/channels/[id]/videos/page.tsx` を作成。  
   - チャンネル名（ダミー）＋テーブル＋ソート/フィルタ UI を配置し、後で `getChannelVideos` を差し込めるようにする。
5. **グラフ用コンポーネントの雛形**  
   - `components/features/charts/TopVideosChart.tsx` と `MonthlyViewsChart.tsx` を作り、Recharts でダミーデータを描画しておく。  
   - props は `Video[]` を受け取る想定にし、「配列を渡せばフロントで可視化まで完結する」契約を敷いておく。

### 今日〜数日で進めたいタスク候補
- `.env.local` と `lib/api.ts` の整備
- `/channels/import` ページ＆フォームコンポーネント実装
- `/channels` 一覧ページのモック実装

※ ここまで完了すれば、ざわ側は Lambda/RDS 実装に集中でき、React 側のルーティングも固まるため、codeX へのタスク切り出しが容易になります。

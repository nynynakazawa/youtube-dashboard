# YouTube チャンネル解析ダッシュボード – Frontend Plan (Fixed)

**目的**  
バックエンド（API Gateway + Lambda + RDS/DynamoDB）が提供する REST API をフロント（Next.js/React）から利用し、  
「チャンネル登録 → 取得結果表示 → 動画一覧 → 簡易グラフ」までを完了させる。  
**本プランの仕様は固定。逸脱・再設計・ライブラリ変更は禁止。**

---

## 0. 技術選定（固定・変更不可）

- Framework: **Next.js 14+ (App Router)**  
- 言語: **TypeScript**  
- スタイリング: **Tailwind CSS**（shadcn/ui 等の UI ライブラリは不使用）  
- グラフ: **Recharts**  
- データ取得: **TanStack Query (React Query)**  
- 状態管理: **最小限（必要箇所のみ useState / useMemo）**  
- Lint/Format: **ESLint + Prettier**（標準設定）  
- テスト: **React Testing Library + Vitest**（最小限、重要画面のみ）  
- モック: **MSW**（開発時のみ任意。`.env.local` に `NEXT_PUBLIC_API_BASE_URL` が無ければ自動でモック有効化）

---

## 1. API コントラクト（固定・変更不可）

- `POST /channels/import`  
  - Body: `{ "channelUrlOrId": string }`  
  - 200: `{"channel": {...}, "summary": {...}}`（要件定義の例に準拠）  
  - 400/404/429/500: メッセージを UI に日本語表示（下記エラーメッセージ規定）

- `GET /channels`  
  - Query: `q?`, `limit`, `offset`  
  - 200: `{ items: [...], totalCount: number }`

- `GET /channels/{id}`  
  - 200: `{"channel": {...}, "summary": {...}}`

- `GET /channels/{id}/videos`  
  - Query: `sort`, `limit`, `offset`, `from`, `to`, `minViews`  
  - 200: `{ items: [...], totalCount: number }`

- `GET /channels/{id}/stats/summary`  
  - Query: `from`, `to`  
  - 200: `{ totalViews, totalLikes, totalComments, monthly: [{month, views}] }`

**API ベース URL**: `process.env.NEXT_PUBLIC_API_BASE_URL` を必須使用（直書き禁止）。

---

## 2. 画面/ルーティング（固定・変更不可）

- `/`（ホーム）
  - 「チャンネル登録フォーム」
    - Input: `チャンネル URL または ID`
    - バリデーション:
      - 未入力 → 「チャンネルURLまたはIDを入力してください」
      - `youtube.com` 含む場合は正規表現で `@handle` または `channel/UC...` を抽出
      - それ以外はテキストをそのまま API に送る
    - 送信 → `POST /channels/import`
  - 成功時: チャンネル名・登録者数・総再生数・動画数・最終取得時刻をカード表示
  - 失敗時: ステータス別にトースト表示（下記メッセージ規定）

- `/channels`（一覧）
  - `GET /channels`
  - 検索（`q`）、ページング（limit=20, offset）
  - テーブル表示（タイトル / 登録者数 / 総再生数 / 動画数）
  - 行クリック → `/channels/[id]` へ遷移

- `/channels/[id]`（チャンネル詳細）
  - `GET /channels/{id}` で概要表示
  - グラフ:
    - 「再生回数トップ10動画のバーグラフ」
    - 「月別総再生数推移（棒 or 折れ線いずれも可、Recharts）」
  - 下部に「動画一覧へ」リンク

- `/channels/[id]/videos`（動画一覧）
  - `GET /channels/{id}/videos`
  - 表示項目：サムネ / タイトル（YouTubeへ新規タブ）/ 投稿日時 / 再生数 / 高評価数 / コメント数 / 長さ（mm:ss）
  - ソート: 投稿日時 / 再生数 / 高評価数 / コメント数（昇降可）
  - フィルタ: 期間 `from~to`, 最低再生数 `minViews`
  - ページング: 1ページ 20件（クエリで変更可）

---

## 3. コンポーネント規定（固定・変更不可）

- `components/Layout.tsx` … 共通レイアウト（ヘッダ・フッタ・コンテナ）
- `components/ChannelImportForm.tsx` … ホーム用フォーム
- `components/StatsCards.tsx` … サマリカード（登録者数・総再生数等）
- `components/VideoTable.tsx` … 動画テーブル（ソート/フィルタ/ページング）
- `components/charts/Top10ViewsBar.tsx` … トップ10棒グラフ
- `components/charts/MonthlyViewsChart.tsx` … 月別推移
- `components/ui/Toast.tsx` … トースト（成功/警告/エラー）
- `lib/api.ts` … フェッチ共通（ベースURL, エラーハンドリング）
- `lib/types.ts` … API レスポンス型（要件定義の JSON に一致）
- `lib/format.ts` … 日付/数値/時間（mm:ss）フォーマッタ

**アクセシビリティ**  
- 画像には `alt` 必須。ボタンには `aria-label` 必須。フォームには `label` を関連付け。

---

## 4. エラーメッセージ規定（固定・変更不可）

- 400: **「入力内容が正しくありません。チャンネルURLまたはIDを確認してください。」**
- 404: **「チャンネルが見つかりませんでした。」**
- 429: **「短時間に更新しすぎです。しばらくしてからお試しください。」**
- 500/その他: **「サーバーで問題が発生しました。時間をおいて再度お試しください。」**

---

## 5. .env 設定（固定・変更不可）

- `.env.local`
  - `NEXT_PUBLIC_API_BASE_URL="https://{api-id}.execute-api.{region}.amazonaws.com/prod"`
  - 未設定の場合は **MSW モックを有効化**（開発者体験向上のため）

---

## 6. スクリプト

- `dev`: 開発サーバ（MSW 自動起動）
- `build`: ビルド
- `start`: 本番起動
- `test`: 単体テスト（最低限）
- `lint`, `format`: 静的解析/整形

---

## 7. 受け入れ基準（Definition of Done）

1) **ホーム**で ID/URL を入力 → 成功時カード表示／失敗時トースト表示（文言一致）  
2) **/channels** で検索・ページングが動作  
3) **/channels/[id]** で 2 種類のグラフが表示（Recharts 使用）  
4) **/channels/[id]/videos** でテーブルのソート/フィルタ/ページングが動作  
5) 画像クリックで YouTube 動画が新規タブで開く  
6) `.env.local` 未設定でもモックで全画面がデモ動作  
7) Lighthouse アクセシビリティ スコア 90+（ローカルで測定）  
8) ESLint 0 エラー / Prettier 済み / `test` が通る  

---

## 8. ディレクトリ構成（完成形）



/src
/app
/(routes)
page.tsx # /
/channels/page.tsx # /channels
/channels/[id]/page.tsx
/channels/[id]/videos/page.tsx
/components
Layout.tsx
ChannelImportForm.tsx
StatsCards.tsx
VideoTable.tsx
/charts
Top10ViewsBar.tsx
MonthlyViewsChart.tsx
/ui
Toast.tsx
/lib
api.ts
types.ts
format.ts
/mocks
handlers.ts # MSW
browser.ts
/tests
home.test.tsx
videos.test.tsx
/styles
globals.css


**本プラン通りに実装し、逸脱しないこと。**

🎯 codeX 用 “マスタープロンプト”（このまま最初に投げる）

下を 1メッセージ丸ごと codeX に送ってください。以降は「タスク別プロンプト」を順番に投げれば進みます。

[システム/方針]
あなたはフロントエンド実装エージェントです。要件は docs/plan.md に完全固定されています。
ライブラリ選定・設計・UI 文言・API 仕様の変更、独断の判断は一切禁止。
出力は Next.js 14 App Router + TypeScript + Tailwind + Recharts + TanStack Query のコードとドキュメントのみ。
必ず 以下を順に完了させ、各ステップで生成物（コード全文）を提示しなさい。

[与件]

本リポジトリに docs/plan.md があり、記載内容が唯一の正解。

API は REST（ベース URL は NEXT_PUBLIC_API_BASE_URL）。未設定なら MSW モックで動作させること。

受け入れ基準（DoD）は docs/plan.md の通り。

[出力要件 共通]

生成物はファイルパス付きで提示（例: src/app/page.tsx: で開始）。

省略禁止。動く最小完結コードを毎回フルで出力。

追加のライブラリは事前明記し、package.json に反映。

ESLint/Prettier で整形済の体裁で出力。

[実行タスク]

初期化:

package.json / tsconfig.json / .eslintrc / .prettierrc / postcss.config.js / tailwind.config.ts / src/styles/globals.css

Next.js App Router セットアップ、Tailwind 初期化

src/lib と src/components の空ファイル雛形

MSW セットアップ（.env.local 未設定時に自動起動）

README.md（起動手順、環境変数、モックの使い方）

基盤コード:

src/lib/api.ts（ベースURL/エラー処理/型付け）

src/lib/types.ts（要件の JSON に一致）

src/lib/format.ts（日時/数値/秒→mm:ss）

src/components/Layout.tsx / ui/Toast.tsx

ホーム /:

ChannelImportForm.tsx + app/page.tsx

バリデーション・トースト・成功カード表示

/channels:

検索 + ページング可能なリスト

/channels/[id]:

概要カード + Top10ViewsBar / MonthlyViewsChart

/channels/[id]/videos:

VideoTable.tsx（ソート/フィルタ/ページング）

テスト:

tests/home.test.tsx / tests/videos.test.tsx（最低限）

微調整:

Lighthouse アクセシビリティ改善（alt/aria/label）

DoD の全項目を満たす

開始: タスク1の生成物をすべて提示せよ。
禁止: 設計変更・仕様提案・分岐質問・保留。迷った場合は必ず docs/plan.md に従う。

▶ タスク別プロンプト（順番に投げるだけ）
① 初期化
タスク1を実行。Next.js 14 App Router + TS + Tailwind の初期セット、MSW 構成、README を含む初期ファイル一式をフル出力。`docs/plan.md` に厳密準拠。省略禁止。ファイルパス明記で。

② 基盤コード
タスク2を実行。`src/lib/api.ts`, `types.ts`, `format.ts`, `components/Layout.tsx`, `components/ui/Toast.tsx` をフル出力。APIエラーをHTTPステータスで日本語メッセージにマッピング。省略禁止。

③ ホーム（/）
タスク3を実行。ホーム画面のフォーム実装と連携。未入力バリデーション文言、400/404/429/500 のトースト文言は plan.md の規定通り。成功時カード表示まで。フルコード出力。

④ チャンネル一覧（/channels）
タスク4を実行。`GET /channels` で検索とページングが機能するテーブルを実装。1ページ20件。行クリックで詳細へ。フルコード出力。

⑤ 詳細 + グラフ（/channels/[id]）
タスク5を実行。`GET /channels/{id}` で概要カード表示。Recharts でトップ10バー / 月別推移を実装。フルコード出力。

⑥ 動画一覧（/channels/[id]/videos）
タスク6を実行。`GET /channels/{id}/videos` 表のソート（投稿・再生・高評価・コメント 昇降）、フィルタ（from/to, minViews）、ページング実装。サムネクリックでYouTubeを新規タブ。長さはmm:ss表示。フルコード出力。

⑦ テスト
タスク7を実行。React Testing Library + Vitest でホーム/動画一覧の最小テストを追加。MSW でAPIモック。`npm test` で通ること。フルコード出力。

⑧ 最終調整
タスク8を実行。Lighthouse アクセシビリティ90+を目標にalt/aria/label整備。DoD全項目のチェックリストを`README.md`末尾に追記。変更差分のみでなく、最終状態の該当ファイル全文を出力。

🔒 実装時の細則（codeX が迷わないための固定ルール）

UI 文言は日本語固定。 英語 UI 禁止。

数値は桁区切り表示（1,234,567）。 日付は YYYY/MM/DD HH:mm（ローカルタイムで OK）。

ローディング状態：スケルトンを必ず表示。空データは「データがありません」。

失敗時：必ずトースト表示 + 画面操作は継続可能。

リンク：サムネ/タイトルは target="_blank" rel="noopener noreferrer"。

グラフ：凡例・ツールチップあり、X/Y 軸ラベルを付与。

型安全：API レスポンスは lib/types.ts で厳格に型付け。any 禁止。

CSS：Tailwind のユーティリティのみ。カスタム CSS は globals.css の最小限に限定。

コミット/PR はこのプロンプト外（出力はファイル全文）。

✅ 提出物チェック（受け入れ時に使う短い表）

 .env.local を消してもモックで動く

 400/404/429/500 のトースト文言が仕様通り

 / 登録 → カード表示できる

 /channels 検索 + ページング動作

 /channels/[id] 2種グラフ表示

 /channels/[id]/videos ソート/フィルタ/ページング動作

 画像クリックで YouTube 新規タブ

 ESLint/Prettier OK、npm test OK、アクセシビリティ90+

このセットで 「判断なしに codeX をドライブ」 できる。
フロントが形になったら、Streamlit 側の “同様の固定プロンプト” も用意できる。次は Analyst 向けの計測ビュー（曜日×時間帯ヒートマップ等）の仕様を同じスタイルで固めよう。

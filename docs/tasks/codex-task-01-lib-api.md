# タスク: API 基盤整備（lib/api.ts + .env.local）

## ゴール
- lib/api.ts に importChannel / getChannels / getChannelVideos を TypeScript で実装し、全 API 呼び出しをここ経由にする。
- .env.local で NEXT_PUBLIC_API_BASE_URL を設定できるようにし、CodeX が環境変数の扱いを理解できる状態にする。

## 前提
- リポジトリ: 
ynynakazawa/youtube-dashboard
- ブランチ: eature/update-dashboard
- 仕様: docs/plan.md, docs/zawa-backend-spec.md

## 要件
- ベース URL は process.env.NEXT_PUBLIC_API_BASE_URL から組み立てる。未設定時は例外を投げる。
- importChannel は POST /channels/import、getChannels は GET /channels、getChannelVideos は GET /channels/{id}/videos を呼ぶ。
- 型は 	ypes/channel.ts / 	ypes/video.ts を使用する前提でダミー宣言しておいてよい。
- fetch ラッパーはエラー時に docs/api-error-contract.md に沿ったメッセージを返す。
- .env.local.example を追加して変数名を周知する。

## 出力フォーマット
- Summary（やったこと）
- 変更ファイルごとの最終コード全文
- Notes（必要なら）

この内容を docs/codex-system-prompt.md と一緒に CodeX に渡す。

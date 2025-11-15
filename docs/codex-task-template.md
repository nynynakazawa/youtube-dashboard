# CodeX タスク用テンプレート

このテンプレートに作業概要を差し替えて、CodeX にそのまま送信してください。

---

# タスク: /channels/import ページの実装

## ゴール
- `app/(routes)/channels/import/page.tsx` にチャンネル登録フォームを実装し、`lib/api.ts` の `importChannel` 経由で `POST /channels/import` を呼び出せるようにする。
- 成功時は同ページ内にチャンネル情報＋summary をカードで表示する。

## 前提
- リポジトリ: `nynynakazawa/youtube-dashboard`
- ブランチ: `feature/update-dashboard`
- 仕様: `docs/plan.md`
- API 仕様: `docs/plan.md`, `docs/zawa-backend-spec.md` の `POST /channels/import`

## 要件
- バリデーション: 未入力時に「チャンネルURLまたはIDを入力してください」と表示
- ローディング中はボタンを disabled にし、「読み込み中…」などの表示を行う
- エラー時はレスポンスメッセージ（あれば）を表示（なければ汎用メッセージ）
- スタイルは Tailwind でシンプルに
- `lib/api.ts` に `importChannel` が未実装の場合は追加してよい

## 出力フォーマット
1. **Summary**
2. **変更したファイルごとの最終コード全文**
3. **Notes（必要なら）**

---

※ タスクごとにタイトルと要件を置き換えて利用してください。複数タスクを同時に依頼する場合は、このテンプレを複数並べるか、見出しを変えて1メッセージにまとめてください。

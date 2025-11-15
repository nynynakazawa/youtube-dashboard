---
name: 'BACKEND: /channels/import ダミーLambda'
about: 'ざわ向け /channels/import のスタブ実装タスク'
title: 'BACKEND: /channels/import ダミーLambda'
labels: backend
assignees: ''
---

## ゴール
- POST /channels/import を受け取り、仕様に沿ったサンプル JSON を返す AWS Lambda を実装する。
- 現時点では YouTube API / RDS / DynamoDB との連携は不要。ハードコーディングレスポンスで構わない。

## やること
1. Lambda ハンドラーを作成（Python）。
2. channelUrlOrId の未入力チェックのみ実装。
3. 固定の channel + summary JSON を返す。
4. API Gateway or SAM ローカルでの動作確認。

## 受け入れ条件
- docs/zawa-backend-spec.md にあるレスポンス形式と一致している。
- 400 エラー時は docs/api-error-contract.md に沿った JSON を返す。
- README か Issue コメントでテスト手順を共有する。

## メモ
- 後続タスクでこのダミーを本実装に差し替える。
- 必要なら .env や IAM 権限の TODO を残しておいて OK。

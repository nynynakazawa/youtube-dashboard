✅ Zawa Backend Specification (Backend担当 完全版)
この文書は ざわ（野澤研究）担当範囲のすべて をまとめた 技術仕様書（.md） です。

フロント（React/Next.js + API Gateway）
→ ZETTAi 担当
バックエンド（Lambda + RDS + DynamoDB + Streamlit）
→ ざわ担当

# 🎯 0. ざわ担当範囲の全体像
[フロント] ZETTAi
  ↓ HTTP(JSON)
[API Gateway] ZETTAi
  ↓
------------------------------
      ▼ ▼ ▼ ここから下 ざわ担当 ▼ ▼ ▼
------------------------------
[Lambda (Python)]
  ├ YouTube Data API 呼び出し
  ├ DynamoDB (更新キャッシュ)
  └ RDS Proxy → RDS(本データ)

[Streamlit]
  └ RDS を直接読み取り、分析ダッシュボードを提供

# 📦 1. バックエンドの構成（ざわ担当）
■ 使用サービス

| サービス | 用途 |
| --- | --- |
| AWS Lambda | API の実処理 (import / get / list) |
| RDS (MySQL/PostgreSQL) | チャンネル・動画・統計の保存 |
| RDS Proxy | Lambda からの安定接続 |
| DynamoDB | channel_update_cache の保存 |
| YouTube Data API | データ取得 |
| Streamlit | RDS を直接読む分析 UI |

# 📁 2. ディレクトリ構成（Backend）
```
backend/
  ├ handlers/
  │   ├ channel_import.py          # POST /channels/import
  │   ├ get_channels.py            # GET /channels
  │   └ get_channel_videos.py      # GET /channels/{id}/videos
  │
  ├ services/
  │   ├ youtube_client.py          # YouTube API ロジック
  │   ├ channel_service.py         # RDSへの書き込み/読み取り
  │   └ stats_service.py           # 統計関連（必要なら）
  │
  ├ db/
  │   ├ rds.py                     # RDS Proxy への接続
  │   └ dynamodb_cache.py          # DynamoDB アクセス
  │
  ├ common/
  │   ├ models.py                  # Pydanticデータモデル
  │   └ response.py                # 共通レスポンス形式
  │
  ├ utils/
  │   └ extract_channel_id.py      # URL→channelId 抽出ロジック
  │
  └ requirements.txt
```

# 🔧 3. ざわ担当 API の仕様（Lambda）
## ⭐ POST /channels/import
● 役割  
URL or channelId を受け取り

- DynamoDB を見て「最近取得していないか」確認
- YouTube API から  
  - チャンネル情報  
  - 動画一覧  
  - 各動画の stats  
  を取得
- RDS に save / upsert
- DynamoDB に更新時刻を記録

### Lambda 擬似コード（Python）
```python
def handler(event, context):
    body = json.loads(event["body"])
    channel_input = body.get("channelUrlOrId")

    # 入力チェック
    if not channel_input:
        return error(400, "チャンネルURLまたはIDを入力してください")

    # URL → channelId 抽出（utils.extract_channel_id）
    channel_id = extract_channel_id(channel_input)
    if not channel_id:
        return error(400, "チャンネルID抽出に失敗しました")

    # DynamoDBでレート制限確認
    cached = dynamo.get(channel_id)
    if cached and is_within_interval(cached["last_fetched_at"]):
        # RDSから現行データを返す
        return success(channel_service.get_summary(channel_id))

    # YouTube API 呼び出し
    yt = YouTubeClient(API_KEY)
    channel_data = yt.get_channel(channel_id)
    video_list = yt.get_all_videos(channel_id)

    # RDSに保存（UPSERT）
    channel_service.upsert_channel(channel_data)
    channel_service.upsert_videos(video_list)

    # DynamoDB 更新
    dynamo.put(channel_id, now(), etag=channel_data["etag"])

    # 最新集計を返す
    summary = channel_service.get_summary(channel_id)
    return success(summary)
```

# 🗄 4. RDS（データベース）仕様
すべて ざわ担当

■ テーブル一覧

- channels
- videos
- video_stats_history

（すべて前のメッセージで提示した通り）

必要なら MySQL/PostgreSQL 向けにそのまま使える CREATE TABLE 文 も書ける。

# 🧩 5. DynamoDB（ざわ担当）
■ テーブル：channel_update_cache

| 属性 | 型 | 説明 |
| --- | --- | --- |
| youtube_channel_id | String | PK |
| last_fetched_at | Number | Unix ms |
| etag | String | 差分更新用 |

用途：

- 更新間隔チェック（例: 10分以内なら取得しない）
- YouTube API へのアクセス最適化

# 🧠 6. YouTube Data API ロジック（ざわ担当）
● 必要な API

- channels.list
- playlistItems.list
- videos.list

● 処理ステップ

1. channelId からチャンネル基本情報取得
2. uploadPlaylistId を取得
3. 再帰的に全動画取得（ページング対応）
4. videos.list に videoId 群を渡して stats 一括取得

# 📊 7. Streamlit（ざわ担当）
● データ取得  
Streamlit → RDS（直）

● 提供する分析機能

- 指標選択
- 曜日 × 時間帯ヒートマップ
- 長さ vs 再生数
- 30日成長カーブ比較
- タグ別パフォーマンス

# 🔥 8. 必要な環境変数（ざわ担当）
```
YOUTUBE_API_KEY=********
DB_HOST=rds-proxy.xxxxxxxx.ap-northeast-1.rds.amazonaws.com
DB_USER=xxx
DB_PASSWORD=xxx
DB_NAME=analytics
MIN_FETCH_INTERVAL=600  # 10 minutes
```

# 📝 9. ざわの責務まとめ
- Lambda（全3〜5関数）の実装
- YouTube API クライアント
- RDS モデル / SQL / インサート・アップサート
- DynamoDB レート制御
- Streamlit ダッシュボード
- バックエンド全ロジック

# 🚀 10. 次のステップ
- RDS の CREATE TABLE 文を生成（必要ならすぐ書く）
- Lambda ハンドラーの実コード化
- YouTube API クライアントの作成
- Streamlit プロトタイプを作成

必要なら：

- Terraform / CDK で AWS 全自動構築
- Lambda デプロイパッケージ
- YouTube API モック
- ローカルテスト環境（LocalStack）

もぜんぶ作れる。

もし「レン（ZETTAi）用の md ももっと詰めて書いて！」
「2人用の GitHub Projects / Issue 設計して！」
などが欲しければ言ってね。

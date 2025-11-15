# YouTube チャンネル解析ダッシュボード - バックエンド開発プロンプト（ざわ担当）

## プロジェクト概要

このプロジェクトは、YouTubeチャンネルの公開情報（動画一覧、視聴数、いいね数など）を自動取得し、ダッシュボードで可視化するシステムです。

**あなたの担当範囲：バックエンド開発**
- AWS Lambda（Python）によるAPI実装
- RDS（MySQL/PostgreSQL）データベース設計・実装
- DynamoDBによるキャッシュ制御
- YouTube Data API連携
- Streamlitによる分析ダッシュボード

**フロントエンド担当：れん（ZETTAi）**
- React/Next.jsによるUI実装
- API Gateway設定
- フロントエンドからのAPI呼び出し

---

## アーキテクチャ全体像

```
[フロント] React/Next.js（れん担当）
  ↓ HTTP(JSON)
[API Gateway]（れん担当）
  ↓
------------------------------
      ▼ ▼ ▼ バックエンド（あなたの担当） ▼ ▼ ▼
------------------------------
[Lambda (Python)]
  ├─ YouTube Data API 呼び出し
  ├─ DynamoDB (更新キャッシュ)
  └─ RDS Proxy → RDS(本データ)

[Streamlit]
  └─ RDS を直接読み取り、分析ダッシュボードを提供
```

---

## コーディング規約（必須遵守）

このプロジェクトでは以下の原則に従ってコードを記述してください。

### 1. 宣言的なコード（Declarative Code）
- 命令的な実装（how）ではなく、何をしたいか（what）を明確に表現する
- 状態の変更は明示的に行い、副作用を最小限に抑える
- ループ処理は`map`、`filter`、`reduce`などの関数型メソッドを使用
- 条件分岐は早期リターンを活用して可読性を向上させる

### 2. DRY原則（Don't Repeat Yourself）
- 同じロジックやコードの重複を避ける
- 3回以上使用されるコードは関数として抽出する
- 共通のユーティリティ関数は`utils/`ディレクトリに配置
- 定数や設定値は`constants/`に集約
- 型定義の重複を避け、共通の型は`types/`ディレクトリに配置

### 3. 拡張を見据えたコード設計
- 将来の機能追加や変更を考慮した柔軟な設計を心がける
- インターフェースや抽象化を適切に使用し、実装の詳細を隠蔽する
- 設定や環境変数は外部化し、ハードコーディングを避ける
- 単一責任の原則（SRP）に従い、各モジュールは一つの責任のみを持つ
- 依存性の注入やファクトリーパターンを活用して結合度を下げる

### 4. 無駄なフォールバックはしない
- 不要なデフォルト値やフォールバック処理を追加しない
- エラーハンドリングは必要最小限に留める
- 過度なnullチェックは避ける（Pythonの型ヒントを活用）
- 実際にエラーが発生する可能性がある箇所のみエラーハンドリングを実装
- 不要なtry-catchブロックは使用しない

### 5. 不要なコードやファイルの削除
- 使用されていないインポート、変数、関数は削除する
- コメントアウトされたコードは削除する
- 未使用のファイルやディレクトリは削除する
- デッドコードや到達不可能なコードは削除する
- 一時的なデバッグコードやprint文は本番コードに残さない

### 6. 分かりやすいルール化された階層構造
- プロジェクトのディレクトリ構造は一貫性を保つ
- ファイル名は明確で一貫した命名規則に従う（`snake_case` for Python）
- 関連するファイルは同じディレクトリに配置する
- ディレクトリ名は複数形を使用（例: `handlers/`, `services/`, `utils/`）

---

## ディレクトリ構造

```
backend/
  ├ handlers/                    # Lambdaハンドラー関数
  │   ├ channel_import.py        # POST /channels/import
  │   ├ list_channels.py          # GET /channels（チャンネル一覧）
  │   ├ get_channel_detail.py     # GET /channels/{id}（チャンネル詳細）
  │   └ get_channel_videos.py    # GET /channels/{id}/videos
  │
  ├ services/                    # ビジネスロジック層
  │   ├ youtube_client.py        # YouTube API ロジック
  │   ├ channel_service.py       # RDSへの書き込み/読み取り
  │   └ stats_service.py         # 統計関連（必要なら）
  │
  ├ db/                          # データベースアクセス層
  │   ├ rds.py                   # RDS Proxy への接続
  │   └ dynamodb_cache.py        # DynamoDB アクセス
  │
  ├ common/                      # 共通モジュール
  │   ├ models.py                # Pydanticデータモデル
  │   └ response.py              # 共通レスポンス形式
  │
  ├ utils/                       # ユーティリティ関数
  │   └ extract_channel_id.py    # URL→channelId 抽出ロジック
  │
  ├ types/                       # 型定義
  │   └ channel.py               # チャンネル関連の型
  │
  ├ constants/                   # 定数
  │   └ config.py                # 設定値
  │
  └ requirements.txt
```

---

## 命名規則

- **関数・変数**: `snake_case`（例: `get_channel_data`）
- **クラス**: `PascalCase`（例: `YouTubeClient`）
- **定数**: `UPPER_SNAKE_CASE`（例: `MIN_FETCH_INTERVAL`）
- **型・インターフェース**: `PascalCase`（例: `ChannelData`）
- **ファイル名**: `snake_case`（例: `channel_import.py`）

---

## インポート順序

1. 標準ライブラリ（`json`, `datetime`など）
2. 外部ライブラリ（`boto3`, `requests`, `pydantic`など）
3. 内部モジュール（`from services import ...`）
4. 型インポート（`from typing import ...`）

---

## 実装要件

### 1. Lambda関数実装

#### POST /channels/import

**役割:**
- URLまたはchannelIdを受け取り、YouTube Data APIからチャンネル情報と動画一覧を取得
- DynamoDBで更新間隔をチェック（MIN_FETCH_INTERVAL: 10分）
- RDSにupsert
- JSONでレスポンスを返す

**処理フロー:**
1. リクエストボディから`channelUrlOrId`を取得
2. 入力バリデーション（未入力チェック）
3. URL → channelId抽出（`utils.extract_channel_id`）
4. DynamoDBでレート制限確認
   - `last_fetched_at`がMIN_FETCH_INTERVAL以内なら、RDSから既存データを返す
5. YouTube Data API呼び出し
   - `channels.list`でチャンネル基本情報取得
   - `playlistItems.list` + `videos.list`で動画一覧とstats取得
6. RDSにupsert（`channel_service.upsert_channel`, `channel_service.upsert_videos`）
7. DynamoDBに`last_fetched_at`と`etag`を更新
8. レスポンス返却

**レスポンス例:**
```json
{
  "channel": {
    "id": 1,
    "youtubeChannelId": "UCxxxxx",
    "title": "サンプルチャンネル",
    "description": "説明文",
    "publishedAt": "2018-05-01T00:00:00Z",
    "subscriberCount": 12345,
    "videoCount": 100,
    "viewCount": 987654
  },
  "summary": {
    "totalViews": 987654,
    "totalVideos": 100,
    "lastFetchedAt": "2025-11-15T12:34:56Z"
  }
}
```

**エラーレスポンス:**
エラーレスポンスは以下の形式で返す:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ"
  }
}
```

**エラーコード:**
- 400: パラメータ不正（チャンネルID抽出失敗など）
  - `message`: "チャンネルID抽出に失敗しました"
- 404: YouTube APIでチャンネルが見つからない、またはRDSにチャンネルが存在しない
  - `message`: "指定されたチャンネルが見つかりませんでした"
- 429: 更新間隔制限に抵触（MIN_FETCH_INTERVAL未満）
  - `message`: "短時間に更新しすぎです。しばらく待ってから再度お試しください"
- 500: 内部エラー
  - `message`: "サーバーエラーが発生しました。しばらく待ってから再度お試しください"

#### GET /channels

**役割:**
- 登録済みチャンネル一覧を返す

**クエリパラメータ:**
- `q`: タイトル部分一致検索（任意）
- `limit`: 取得件数（デフォルト: 20）
- `offset`: オフセット（デフォルト: 0）

**レスポンス例:**
```json
{
  "items": [
    {
      "id": 1,
      "youtubeChannelId": "UCxxx",
      "title": "サンプル",
      "subscriberCount": 1000,
      "viewCount": 123456,
      "videoCount": 10
    }
  ],
  "totalCount": 5
}
```

#### GET /channels/{id}

**役割:**
- チャンネル詳細 + 直近のサマリを返す

**パスパラメータ:**
- `id`: チャンネルID（数値）

**レスポンス例:**
```json
{
  "channel": {
    "id": 1,
    "youtubeChannelId": "UCxxx",
    "title": "サンプルチャンネル",
    "description": "説明文",
    "publishedAt": "2018-05-01T00:00:00Z",
    "subscriberCount": 12345,
    "videoCount": 100,
    "viewCount": 987654
  },
  "summary": {
    "totalViews": 987654,
    "totalVideos": 100,
    "lastFetchedAt": "2025-11-15T12:34:56Z"
  }
}
```

#### GET /channels/{id}/videos

**役割:**
- 指定チャンネルの動画一覧を返す

**クエリパラメータ:**
- `sort`: ソート条件（`views_desc`, `views_asc`, `likes_desc`, `comments_desc`, `date_desc`, `date_asc`）
- `limit`: 1ページあたりの件数（デフォルト: 20）
- `offset`: オフセット（デフォルト: 0）
- `from`: 開始日（YYYY-MM-DD形式）
- `to`: 終了日（YYYY-MM-DD形式）
- `minViews`: 最低再生数

**レスポンス例:**
```json
{
  "items": [
    {
      "id": 123,
      "youtubeVideoId": "abcd1234",
      "title": "動画タイトル",
      "thumbnailUrl": "https://i.ytimg.com/vi/abcd1234/hqdefault.jpg",
      "publishedAt": "2024-07-01T12:00:00Z",
      "durationSec": 600,
      "latestStats": {
        "viewCount": 123456,
        "likeCount": 2345,
        "commentCount": 123
      }
    }
  ],
  "totalCount": 100
}
```

### 2. RDSデータベース設計

#### channels テーブル

```sql
CREATE TABLE channels (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  youtube_channel_id VARCHAR(64) UNIQUE NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  published_at TIMESTAMP,
  subscriber_count BIGINT,
  video_count INT,
  view_count BIGINT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_youtube_channel_id (youtube_channel_id)
);
```

#### videos テーブル

```sql
CREATE TABLE videos (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  channel_id BIGINT NOT NULL,
  youtube_video_id VARCHAR(64) UNIQUE NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  published_at TIMESTAMP NOT NULL,
  duration_sec INT,
  tags_json JSON,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE,
  INDEX idx_channel_id (channel_id),
  INDEX idx_published_at (published_at),
  INDEX idx_channel_published (channel_id, published_at)
);
```

#### video_stats_history テーブル

```sql
CREATE TABLE video_stats_history (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  video_id BIGINT NOT NULL,
  snapshot_at TIMESTAMP NOT NULL,
  view_count BIGINT NOT NULL,
  like_count BIGINT,
  comment_count BIGINT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE,
  INDEX idx_video_snapshot (video_id, snapshot_at)
);
```

### 3. DynamoDBテーブル設計

#### channel_update_cache

**パーティションキー:**
- `youtube_channel_id` (String)

**属性:**
- `last_fetched_at` (Number): Unix time（ミリ秒）
- `etag` (String, 任意): YouTube APIのレスポンスETag

**用途:**
- 更新間隔チェック（MIN_FETCH_INTERVAL: 10分）
- YouTube APIへのアクセス最適化

### 4. YouTube Data API連携

**必要なAPI:**
- `channels.list`: チャンネル基本情報取得
- `playlistItems.list`: アップロード動画一覧取得（ページング対応）
- `videos.list`: 動画の詳細情報とstats取得

**処理ステップ:**
1. `channelId`からチャンネル基本情報取得
2. `uploadPlaylistId`を取得
3. `playlistItems.list`で再帰的に全動画取得（ページング対応）
4. `videos.list`に`videoId`群を渡してstats一括取得

### 5. Streamlit分析ダッシュボード

**データ取得:**
- Streamlit → RDS（直接接続）

**提供する分析機能:**
- チャンネル選択（一覧 or channelId直接入力）
- 指標選択（再生数、いいね数、コメント数）
- 曜日 × 時間帯ヒートマップ（その時間に公開された動画の平均再生数）
- 動画長さ vs 再生数の散布図
- 公開から30日間の成長カーブ比較（複数動画オーバーレイ）
- タグ別の平均パフォーマンス

---

## 環境変数

Lambda関数で必要な環境変数:

```
YOUTUBE_API_KEY=********
DB_HOST=rds-proxy.xxxxxxxx.ap-northeast-1.rds.amazonaws.com
DB_USER=xxx
DB_PASSWORD=xxx
DB_NAME=analytics
MIN_FETCH_INTERVAL=600  # 10 minutes (秒)
DYNAMODB_TABLE_NAME=channel_update_cache
```

---

## 依存関係（requirements.txt）

```
boto3>=1.28.0
requests>=2.31.0
pydantic>=2.0.0
pymysql>=1.1.0  # MySQLの場合
# または
psycopg2-binary>=2.9.0  # PostgreSQLの場合
```

---

## 実装時の注意事項

1. **Lambda関数は薄く保つ**
   - Handler関数は`event`からパラメータを取り出し、service層に渡すだけ
   - ビジネスロジックは`services/`に配置

2. **エラーハンドリング**
   - 適切なレベルでキャッチし、ユーザーに分かりやすいメッセージを返す
   - エラーログは構造化された形式で記録（CloudWatch Logs）

3. **型安全性**
   - Pydanticモデルを使用してリクエスト/レスポンスの型を定義
   - Pythonの型ヒントを活用

4. **パフォーマンス**
   - RDS Proxyを使用して接続プールを管理
   - DynamoDBでレート制限を実装し、不要なAPI呼び出しを避ける

5. **セキュリティ**
   - APIキーはAWS Systems Manager Parameter StoreまたはSecrets Managerに格納
   - RDSへのアクセスはVPC内からのみ
   - ユーザー入力は必ず検証・サニタイズする

---

## 開発手順

1. **Step1**: 最小のLambda（import）を作成
   - 入力を受け取る
   - ダミーJSONを返す
   - → フロントエンドがまず画面を動かせるようにする

2. **Step2**: 実際のYouTube APIとRDS保存を実装

3. **Step3**: 他のAPIエンドポイントを実装（GET /channels（list_channels.py）, GET /channels/{id}（get_channel_detail.py）, GET /channels/{id}/videos）

4. **Step4**: Streamlit分析ツールを作成

---

## 完成像

- 本格的なAWSバックエンド開発経験
- YouTube解析データベース構築
- Streamlit分析
- インターンでもそのまま提出できるレベルの本物プロダクト


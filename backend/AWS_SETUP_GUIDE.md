# AWS設定手順書（GUI操作）

このドキュメントでは、YouTube DashboardのバックエンドをAWS上に構築するための手順をGUI操作で説明します。

## 前提条件

- AWSアカウントを持っていること
- YouTube Data API v3のAPIキーを取得済みであること

---

## 1. RDS（MySQL）データベースの作成

### 1.1 RDSインスタンスの作成

1. AWSコンソールにログインし、**RDS**サービスを開く
2. 左メニューから**データベース**を選択
3. **データベースの作成**ボタンをクリック
4. 以下の設定を行う：
   - **エンジンのオプション**: MySQLを選択
   - **エンジンのバージョン**: 最新の安定版（例: MySQL 8.0）
   - **テンプレート**: 無料利用枠（開発環境の場合）または本番環境用
   - **DB識別子**: `youtube-dashboard-db`
   - **マスターユーザー名**: `admin`（任意）
   - **マスターパスワード**: 強力なパスワードを設定（後で使用します）
   - **DBインスタンスクラス**: `db.t3.micro`（無料枠の場合）または適切なサイズ
   - **ストレージ**: デフォルト設定でOK
   - **接続**: VPC内からのみアクセス可能にする
5. **データベースの作成**ボタンをクリック
6. データベースが作成されるまで待つ（数分かかります）

### 1.2 データベースの初期化

1. RDSコンソールで作成したデータベースを選択
2. **接続とセキュリティ**タブを開く
3. **エンドポイント**をメモしておく（例: `youtube-dashboard-db.xxxxx.ap-northeast-1.rds.amazonaws.com`）
4. ローカル環境またはEC2インスタンスからMySQLクライアントで接続
5. `backend/db/schema.sql`の内容を実行してテーブルを作成

```bash
mysql -h <エンドポイント> -u admin -p < backend/db/schema.sql
```

---

## 2. RDS Proxyの作成

### 2.1 RDS Proxyの作成

1. RDSコンソールで、左メニューから**プロキシ**を選択
2. **プロキシの作成**ボタンをクリック
3. 以下の設定を行う：
   - **プロキシ識別子**: `youtube-dashboard-proxy`
   - **ターゲットグループ**: 新規作成
     - **RDSインスタンス**: 先ほど作成したデータベースを選択
     - **データベース名**: `analytics`（または作成したデータベース名）
   - **認証情報**: Secrets Managerで新しいシークレットを作成
     - シークレット名: `rds-proxy-credentials`
     - ユーザー名: RDSのマスターユーザー名
     - パスワード: RDSのマスターパスワード
   - **VPC**: RDSと同じVPCを選択
   - **サブネット**: 複数のサブネットを選択（可用性のため）
   - **セキュリティグループ**: 新規作成または既存のものを選択
4. **プロキシの作成**ボタンをクリック
5. プロキシのエンドポイントをメモしておく（例: `youtube-dashboard-proxy.proxy-xxxxx.ap-northeast-1.rds.amazonaws.com`）

---

## 3. DynamoDBテーブルの作成

### 3.1 テーブルの作成

1. AWSコンソールで**DynamoDB**サービスを開く
2. **テーブルの作成**ボタンをクリック
3. 以下の設定を行う：
   - **テーブル名**: `channel_update_cache`
   - **パーティションキー**: `youtube_channel_id`（文字列型）
   - **テーブル設定**: デフォルト設定でOK
   - **容量設定**: オンデマンドまたはプロビジョニング済み（無料枠の場合はプロビジョニング済み、読み込み/書き込み容量ユニット: 5）
4. **テーブルの作成**ボタンをクリック

---

## 4. Lambda関数の作成とデプロイ

### 4.1 Lambda関数の作成

1. AWSコンソールで**Lambda**サービスを開く
2. **関数の作成**ボタンをクリック
3. **一から作成**を選択
4. 以下の設定を行う：
   - **関数名**: `youtube-dashboard-channel-import`（最初の関数）
   - **ランタイム**: Python 3.11 または 3.12
   - **アーキテクチャ**: x86_64
5. **関数の作成**ボタンをクリック

### 4.2 Lambda関数のコードアップロード

1. ローカル環境でLambda関数用のZIPファイルを作成：

```bash
cd backend
zip -r lambda-channel-import.zip handlers/ services/ db/ common/ utils/ constants/ -x "*.pyc" "__pycache__/*"
```

2. Lambdaコンソールで、作成した関数を選択
3. **コード**タブを開く
4. **アップロード元**ドロップダウンから**ZIPファイルをアップロード**を選択
5. 作成したZIPファイルをアップロード
6. **ハンドラー**を`handlers.channel_import.lambda_handler`に設定

### 4.3 環境変数の設定

1. Lambda関数の**設定**タブを開く
2. **環境変数**セクションで**編集**をクリック
3. 以下の環境変数を追加：
   - `YOUTUBE_API_KEY`: YouTube Data API v3のAPIキー
   - `DB_HOST`: RDS Proxyのエンドポイント
   - `DB_USER`: RDSのマスターユーザー名
   - `DB_PASSWORD`: RDSのマスターパスワード（またはSecrets Managerから取得）
   - `DB_NAME`: データベース名（例: `analytics`）
   - `MIN_FETCH_INTERVAL`: `600`（10分）
   - `DYNAMODB_TABLE_NAME`: `channel_update_cache`

### 4.4 IAMロールの設定

1. Lambda関数の**設定**タブで**アクセス権限**を開く
2. **ロール名**をクリックしてIAMコンソールを開く
3. **許可を追加** → **ポリシーをアタッチ**を選択
4. 以下のポリシーをアタッチ：
   - `AmazonDynamoDBFullAccess`（または必要最小限の権限）
   - `AmazonRDSDataFullAccess`（または必要最小限の権限）
   - VPCアクセス用のポリシー（VPC内のRDSにアクセスする場合）

### 4.5 VPC設定（RDSにアクセスする場合）

1. Lambda関数の**設定**タブで**VPC**を開く
2. **編集**をクリック
3. 以下の設定を行う：
   - **VPC**: RDSと同じVPCを選択
   - **サブネット**: 複数のサブネットを選択
   - **セキュリティグループ**: RDSにアクセス可能なセキュリティグループを選択
4. **保存**をクリック

### 4.6 他のLambda関数の作成

同様の手順で、以下のLambda関数も作成してください：

- `youtube-dashboard-list-channels`（ハンドラー: `handlers.list_channels.lambda_handler`）
- `youtube-dashboard-get-channel-detail`（ハンドラー: `handlers.get_channel_detail.lambda_handler`）
- `youtube-dashboard-get-channel-videos`（ハンドラー: `handlers.get_channel_videos.lambda_handler`）

各関数に同じ環境変数とIAMロールを設定してください。

---

## 5. API Gatewayの設定（フロントエンド担当者と協力）

### 5.1 HTTP APIの作成

1. AWSコンソールで**API Gateway**サービスを開く
2. **APIの作成**をクリック
3. **HTTP API**を選択して**構築**をクリック
4. **統合の追加**をクリック
5. 各エンドポイントに対してLambda関数を統合：
   - `POST /channels/import` → `youtube-dashboard-channel-import`
   - `GET /channels` → `youtube-dashboard-list-channels`
   - `GET /channels/{id}` → `youtube-dashboard-get-channel-detail`
   - `GET /channels/{id}/videos` → `youtube-dashboard-get-channel-videos`

### 5.2 CORS設定

1. API Gatewayコンソールで、作成したAPIを選択
2. **CORS**セクションで設定：
   - **アクセス制御許可オリジン**: フロントエンドのURL（例: `https://your-domain.com`）
   - **アクセス制御許可メソッド**: `GET`, `POST`
   - **アクセス制御許可ヘッダー**: `Content-Type`
3. **保存**をクリック

---

## 6. Secrets Managerの設定（オプション、推奨）

### 6.1 シークレットの作成

1. AWSコンソールで**Secrets Manager**サービスを開く
2. **新しいシークレットを保存**をクリック
3. **シークレットタイプ**: **その他のシークレット**を選択
4. **キー/値のペア**で以下のシークレットを作成：
   - `youtube-api-key`: YouTube Data API v3のAPIキー
   - `rds-credentials`: RDSのユーザー名とパスワード
5. **シークレット名**: `youtube-dashboard-secrets`
6. **次へ**をクリックして保存

### 6.2 Lambda関数でのSecrets Manager参照

Lambda関数の環境変数で、Secrets Managerから値を取得するように設定するか、コード内でSecrets Manager APIを使用して取得します。

---

## 7. セキュリティグループの設定

### 7.1 Lambda用セキュリティグループ

1. AWSコンソールで**EC2**サービスを開く
2. 左メニューから**セキュリティグループ**を選択
3. **セキュリティグループを作成**をクリック
4. 以下の設定を行う：
   - **名前**: `lambda-rds-access`
   - **説明**: LambdaからRDSへのアクセス用
   - **VPC**: RDSと同じVPCを選択
5. **作成**をクリック

### 7.2 RDS用セキュリティグループ

1. RDSコンソールで、作成したデータベースを選択
2. **接続とセキュリティ**タブを開く
3. **VPCセキュリティグループ**のリンクをクリック
4. **インバウンドルール**タブで**ルールを編集**をクリック
5. 以下のルールを追加：
   - **タイプ**: MySQL/Aurora
   - **ソース**: Lambda用セキュリティグループを選択
   - **説明**: Lambdaからのアクセス許可
6. **ルールを保存**をクリック

---

## 8. 動作確認

### 8.1 Lambda関数のテスト

1. Lambdaコンソールで、各関数を選択
2. **テスト**タブを開く
3. テストイベントを作成して実行：
   - `channel_import`: `{"body": "{\"channelUrlOrId\": \"UCxxxxx\"}"}`
   - `list_channels`: `{"queryStringParameters": {}}`
   - `get_channel_detail`: `{"pathParameters": {"id": "1"}}`
   - `get_channel_videos`: `{"pathParameters": {"id": "1"}, "queryStringParameters": {}}`

### 8.2 API Gatewayのテスト

1. API Gatewayコンソールで、作成したAPIを選択
2. 各エンドポイントを選択して**テスト**をクリック
3. リクエストを送信してレスポンスを確認

---

## 9. トラブルシューティング

### よくある問題

1. **Lambda関数がタイムアウトする**
   - タイムアウト設定を延長（最大15分）
   - メモリサイズを増やす

2. **RDSに接続できない**
   - セキュリティグループの設定を確認
   - VPC設定を確認
   - RDS Proxyの設定を確認

3. **DynamoDBにアクセスできない**
   - IAMロールにDynamoDBの権限があるか確認
   - テーブル名が正しいか確認

4. **YouTube APIのエラー**
   - APIキーが正しいか確認
   - APIキーのクォータを確認

---

## 10. コスト最適化のヒント

1. **RDS**: 開発環境では`db.t3.micro`を使用
2. **Lambda**: 不要な関数は削除
3. **DynamoDB**: オンデマンド容量を使用（低トラフィックの場合）
4. **API Gateway**: HTTP APIを使用（REST APIより安価）

---

## 次のステップ

- Streamlitダッシュボードの実装（`backend/streamlit/`ディレクトリに作成予定）
- CloudWatch Logsでのログ監視設定
- アラームの設定（エラー発生時の通知など）


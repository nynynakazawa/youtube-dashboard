# フロントエンドとバックエンドの接続手順

このドキュメントでは、Next.jsフロントエンド（`app/`）とAWS Lambdaバックエンド（`backend/`）を接続する手順を説明します。

## 前提条件

- AWS_SETUP_GUIDE.mdに従って、以下のリソースが作成済みであること：
  - RDS（MySQL）データベース
  - DynamoDBテーブル（`channel_update_cache`）
  - Lambda関数（4つすべて）
  - API Gateway（HTTP API）

---

## 1. API GatewayのエンドポイントURLを取得

### 1.1 API Gatewayコンソールでエンドポイントを確認

1. AWSコンソールで**API Gateway**サービスを開く
2. 作成したHTTP APIを選択
3. **ステージ**タブを開く（または**統合**タブから**APIエンドポイント**を確認）
4. **デフォルト**ステージ（または作成したステージ）の**呼び出しURL**をコピー
   - 形式: `https://{api-id}.execute-api.{region}.amazonaws.com`
   - 例: `https://abc123xyz.execute-api.ap-northeast-1.amazonaws.com`

**重要**: 
- HTTP APIの場合は、ステージ名がURLに含まれない場合があります
- REST APIの場合は、`/prod`や`/dev`などのステージ名が含まれます
- 実際のエンドポイントURLは、API Gatewayコンソールで確認してください

### 1.2 エンドポイントURLの確認方法（詳細）

**HTTP APIの場合**:
- **統合**タブ → **APIエンドポイント**セクションに表示されるURL
- または、**ステージ**タブ → **デフォルト**ステージの**呼び出しURL**

**REST APIの場合**:
- **ステージ**タブ → ステージ名（例: `prod`）を選択 → **呼び出しURL**
- 形式: `https://{api-id}.execute-api.{region}.amazonaws.com/{stage-name}`

---

## 2. 環境変数の設定

### 2.1 `.env.local`ファイルの作成

プロジェクトルート（`youtube-dashboard/`）に`.env.local`ファイルを作成します。

```bash
# プロジェクトルートに移動
cd /Users/nakazawa/Desktop/個人開発/youtube-dashboard

# .env.localファイルを作成
touch .env.local
```

### 2.2 環境変数の設定

`.env.local`ファイルに以下の内容を記述します：

```bash
# API GatewayのエンドポイントURL
NEXT_PUBLIC_API_BASE_URL=https://{api-id}.execute-api.{region}.amazonaws.com
```

**例**:
```bash
NEXT_PUBLIC_API_BASE_URL=https://abc123xyz.execute-api.ap-northeast-1.amazonaws.com
```

**注意**:
- `{api-id}`と`{region}`は、実際のAPI GatewayのエンドポイントURLに置き換えてください
- HTTP APIの場合は、ステージ名が含まれない場合があります
- REST APIの場合は、ステージ名を含める必要があります（例: `/prod`）

### 2.3 環境変数の確認

`.env.local`ファイルが正しく設定されているか確認します：

```bash
# .env.localの内容を確認（機密情報が含まれるため、注意して確認）
cat .env.local
```

**重要**: 
- `.env.local`ファイルは`.gitignore`に含まれていることを確認してください
- このファイルはGitにコミットしないでください（機密情報が含まれます）

---

## 3. CORS設定の確認と修正

### 3.1 API GatewayのCORS設定を確認

1. API Gatewayコンソールで、作成したAPIを選択
2. **CORS**セクションを開く
3. 以下の設定を確認・設定：

**開発環境の場合**:
- **アクセス制御許可オリジン**: `http://localhost:3000`（Next.jsのデフォルトポート）
- **アクセス制御許可メソッド**: `GET`, `POST`, `OPTIONS`
- **アクセス制御許可ヘッダー**: `Content-Type`, `Authorization`（必要に応じて）

**本番環境の場合**:
- **アクセス制御許可オリジン**: フロントエンドのデプロイ先URL（例: `https://your-domain.com`）
- **アクセス制御許可メソッド**: `GET`, `POST`, `OPTIONS`
- **アクセス制御許可ヘッダー**: `Content-Type`, `Authorization`（必要に応じて）

### 3.1.1 アクセス制御許可メソッドについて

**アクセス制御許可メソッド**は、フロントエンドからバックエンドAPIに対して使用を許可するHTTPメソッドを指定する設定です。

#### このプロジェクトで使用するメソッド

| メソッド | 用途 | このプロジェクトでの使用例 |
|---------|------|---------------------------|
| `GET` | データ取得 | `GET /channels`（チャンネル一覧取得）<br>`GET /channels/{id}`（チャンネル詳細取得）<br>`GET /channels/{id}/videos`（動画一覧取得） |
| `POST` | データ送信・作成 | `POST /channels/import`（チャンネルインポート） |
| `OPTIONS` | プリフライトリクエスト（自動） | ブラウザが自動的に送信（CORS確認用） |

#### その他のHTTPメソッド

以下のメソッドは、このプロジェクトでは現在使用していませんが、将来的に使用する可能性があります：

| メソッド | 用途 | 使用例 |
|---------|------|--------|
| `PUT` | データの完全置換・更新 | `PUT /channels/{id}`（チャンネル情報の更新） |
| `PATCH` | データの部分更新 | `PATCH /channels/{id}`（チャンネル情報の一部更新） |
| `DELETE` | データの削除 | `DELETE /channels/{id}`（チャンネルの削除） |
| `HEAD` | ヘッダー情報のみ取得 | `HEAD /channels`（レスポンスヘッダーのみ取得） |

**注意**:
- `OPTIONS`は必ず含める必要があります（ブラウザが自動的に送信するプリフライトリクエスト用）
- 実際に使用するメソッドのみを許可することで、セキュリティを向上させます
- 将来的に`PUT`や`DELETE`を使用する場合は、CORS設定にも追加してください

### 3.1.2 アクセス制御許可ヘッダーについて

**アクセス制御許可ヘッダー**は、フロントエンドからバックエンドAPIに送信することを許可するHTTPヘッダーを指定する設定です。

#### このプロジェクトで使用するヘッダー

| ヘッダー | 用途 | 説明 |
|---------|------|------|
| `Content-Type` | リクエストボディの形式を指定 | `application/json`を指定してJSONデータを送信する際に使用<br>例: `Content-Type: application/json` |
| `Authorization` | 認証情報を送信 | 将来的に認証機能を追加する場合に使用<br>例: `Authorization: Bearer {token}` |

#### その他のよく使用されるヘッダー

以下のヘッダーは、このプロジェクトでは現在使用していませんが、一般的に使用されるヘッダーです：

| ヘッダー | 用途 | 使用例 |
|---------|------|--------|
| `Accept` | レスポンスの形式を指定 | `Accept: application/json`（JSON形式でレスポンスを要求） |
| `X-Requested-With` | リクエストの種類を識別 | `X-Requested-With: XMLHttpRequest`（Ajaxリクエストであることを示す） |
| `X-API-Key` | APIキーを送信 | `X-API-Key: {api-key}`（APIキー認証） |
| `X-CSRF-Token` | CSRF対策用トークン | `X-CSRF-Token: {token}`（CSRF攻撃を防ぐ） |

#### なぜヘッダーを許可する必要があるのか？

ブラウザのセキュリティポリシーにより、**カスタムヘッダー**（`Content-Type`以外の独自ヘッダー）を含むリクエストを送信する場合、CORS設定でそのヘッダーを明示的に許可する必要があります。

**シンプルなリクエスト**（以下の条件をすべて満たす）:
- メソッド: `GET`, `POST`, `HEAD`のいずれか
- ヘッダー: `Accept`, `Accept-Language`, `Content-Language`, `Content-Type`（`application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`のみ）のみ

**プリフライトリクエストが必要なリクエスト**（上記以外）:
- カスタムヘッダー（`Content-Type: application/json`など）を含む場合
- `PUT`, `DELETE`, `PATCH`などのメソッドを使用する場合

このプロジェクトでは、`POST /channels/import`で`Content-Type: application/json`を使用しているため、プリフライトリクエストが発生し、`Content-Type`ヘッダーを許可する必要があります。

#### 設定の推奨事項

**最小限の原則**:
- 実際に使用するヘッダーのみを許可する
- 不要なヘッダーを許可しないことで、セキュリティを向上させる

**このプロジェクトでの推奨設定**:
- **必須**: `Content-Type`（JSONデータを送信するため）
- **オプション**: `Authorization`（将来的に認証機能を追加する場合）

### 3.2 CORS設定の適用

1. CORS設定を変更した場合は、**保存**をクリック
2. **デプロイ**をクリックして、変更を反映させる
   - **ステージ**: `default`（または作成したステージ）を選択
   - **デプロイ**をクリック

**注意**: CORS設定を変更した場合は、必ずデプロイを実行してください。デプロイしないと変更が反映されません。

---

## 3.5 API Gatewayのルートと統合の設定

### 3.5.1 統合（Integration）とは何か

**統合（Integration）**は、API GatewayのHTTP APIで、リクエストをバックエンドサービス（このプロジェクトではLambda関数）に転送するための設定です。

#### 統合の役割

- **リクエストの転送**: API Gatewayが受け取ったHTTPリクエストを、指定されたLambda関数に転送する
- **レスポンスの返却**: Lambda関数からのレスポンスを、HTTPレスポンスとしてクライアントに返す
- **形式の変換**: HTTPリクエストをLambda関数が理解できる形式（イベント）に変換し、Lambda関数のレスポンスをHTTPレスポンスに変換する

#### 統合の種類

このプロジェクトでは、**AWS_PROXY**統合を使用します：

- **AWS_PROXY**: Lambda関数を直接呼び出す統合タイプ
  - リクエスト全体（ヘッダー、ボディ、パスパラメータなど）がLambda関数の`event`パラメータに渡される
  - Lambda関数のレスポンスがそのままHTTPレスポンスとして返される
  - 最もシンプルで、Lambda関数で柔軟に処理できる

### 3.5.2 ルート（Route）とは何か

**ルート（Route）**は、API Gatewayで定義される**HTTPメソッドとパスの組み合わせ**です。

#### ルートの役割

- **リクエストのマッチング**: クライアントからのリクエストのメソッドとパスに基づいて、どの統合を使用するかを決定する
- **統合への紐付け**: マッチしたルートに対応する統合（Lambda関数）を呼び出す

#### ルートの形式

- **メソッド**: `GET`, `POST`, `PUT`, `DELETE`など
- **パス**: `/channels`, `/channels/{id}`, `/channels/{id}/videos`など
  - `{id}`はパスパラメータで、Lambda関数の`event["pathParameters"]["id"]`で取得できる

### 3.5.3 ルートと統合の関係

```
[クライアント]
  ↓ HTTPリクエスト: POST /channels/import
[API Gateway]
  ↓ ルートでマッチング: POST /channels/import
  ↓ 統合を参照: integrations/xxx
[Lambda関数: youtube-dashboard-channel-import]
  ↓ 処理実行
  ↓ レスポンス返却
[API Gateway]
  ↓ HTTPレスポンス
[クライアント]
```

**重要なポイント**:
- **ルートだけでは動作しない**: ルートは統合に紐付けられていないと、リクエストを処理できない
- **統合だけでは動作しない**: 統合はルートに紐付けられていないと、リクエストを受け取れない
- **両方が必要**: ルートと統合の両方が正しく設定され、紐付けられている必要がある

### 3.5.4 このプロジェクトで必要な統合とルート

以下の4つの統合とルートのペアが必要です：

| ルート | 統合（Lambda関数） |
|--------|-------------------|
| `POST /channels/import` | `youtube-dashboard-channel-import` |
| `GET /channels` | `youtube-dashboard-list-channels` |
| `GET /channels/{id}` | `youtube-dashboard-get-channel-detail` |
| `GET /channels/{id}/videos` | `youtube-dashboard-get-channel-videos` |

### 3.5.5 統合とルートの設定手順（GUI）

#### ステップ1: 統合の作成

1. API Gatewayコンソールで、作成したHTTP APIを選択
2. 左メニューから**統合**を選択
3. **統合を作成**をクリック
4. 各Lambda関数に対して統合を作成：
   - **統合タイプ**: `AWS_PROXY`を選択
   - **Lambda関数**: 対応するLambda関数を選択
   - **統合名**: 任意の名前（例: `channel-import-integration`）
   - **Payload形式バージョン**: `1.0`を選択（HTTP APIでは必須）
   - **作成**をクリック
   - Lambda関数へのアクセス許可を求められたら、**承認**をクリック

#### ステップ2: ルートの作成と統合の紐付け

1. 左メニューから**ルート**を選択
2. **ルートを作成**をクリック
3. 各エンドポイントに対してルートを作成：
   - **メソッド**: `GET`または`POST`を選択
   - **パス**: `/channels`, `/channels/{id}`などを入力
   - **統合**: 上で作成した統合を選択
   - **作成**をクリック

#### ステップ3: デプロイ

1. 左メニューから**デプロイ**を選択
2. **ステージ**: `$default`を選択（または新しいステージを作成）
3. **デプロイ**をクリック

**重要**: ルートと統合を設定した後は、必ずデプロイを実行してください。デプロイしないと変更が反映されません。

### 3.5.6 AWS CLIでの確認方法

統合とルートが正しく設定されているか、AWS CLIで確認できます：

```bash
# API IDを取得
aws apigatewayv2 get-apis --region ap-northeast-1 --query 'Items[*].[ApiId,Name]' --output table

# ルート一覧を確認（統合が紐付けられているか確認）
aws apigatewayv2 get-routes --api-id {api-id} --region ap-northeast-1 --output table --query 'Items[*].[RouteKey,Target]'

# 統合一覧を確認
aws apigatewayv2 get-integrations --api-id {api-id} --region ap-northeast-1 --output json

# 特定のルートの詳細を確認
aws apigatewayv2 get-route --api-id {api-id} --route-id {route-id} --region ap-northeast-1 --output json | jq '{RouteKey, Target}'
```

**正常な状態**:
- すべてのルートの`Target`が`integrations/{integration-id}`の形式になっている
- 統合が4つ存在し、それぞれが正しいLambda関数に紐付けられている

**問題がある状態**:
- ルートの`Target`が`null`になっている → 統合が紐付けられていない
- 統合が存在しない → 統合が作成されていない

---

## 4. Lambda関数のレスポンス形式の確認

### 4.1 レスポンス形式の確認

Lambda関数のレスポンスが、フロントエンドで期待される形式と一致しているか確認します。

**フロントエンドで期待される形式**（`lib/api.ts`参照）:
- 成功時: JSONオブジェクト（APIエンドポイントごとに異なる）
- エラー時: `{ error: { code: number, message: string, details: null } }`

**バックエンドの実装**（`backend/common/response.py`参照）:
- `success_response()`: 成功時のレスポンス形式
- `error_response()`: エラー時のレスポンス形式

### 4.2 レスポンス形式の確認方法

Lambda関数のテストを実行して、レスポンス形式を確認します：

1. Lambdaコンソールで、各関数を選択
2. **テスト**タブを開く
3. テストイベントを作成して実行
4. レスポンス形式を確認

**確認すべきポイント**:
- ステータスコードが正しいか（200, 400, 404, 429, 500など）
- レスポンスボディがJSON形式か
- エラー時の形式が`{ error: { code, message, details } }`になっているか
- CORSヘッダーが含まれているか（`Access-Control-Allow-Origin`など）

---

## 5. 動作確認

### 5.1 開発サーバーの起動

```bash
# プロジェクトルートに移動
cd /Users/nakazawa/Desktop/個人開発/youtube-dashboard

# 開発サーバーを起動
npm run dev
```

### 5.2 ブラウザで動作確認

1. ブラウザで`http://localhost:3000`を開く
2. 各ページでAPI呼び出しが正常に動作するか確認：

**確認すべきページ**:
- `/`（ホーム）: チャンネルインポート機能
- `/channels`: チャンネル一覧
- `/channels/[id]`: チャンネル詳細
- `/channels/[id]/videos`: 動画一覧

### 5.3 ブラウザの開発者ツールで確認

1. ブラウザの開発者ツール（F12）を開く
2. **ネットワーク**タブを開く
3. 各API呼び出しのリクエストとレスポンスを確認：

**確認すべきポイント**:
- リクエストURLが正しいか（`NEXT_PUBLIC_API_BASE_URL`が正しく設定されているか）
- ステータスコードが正しいか（200, 400, 404, 429, 500など）
- CORSエラーが発生していないか
- レスポンスボディが正しい形式か

### 5.4 エラーの確認

**よくあるエラーと対処法**:

1. **CORSエラー**:
   - エラーメッセージ: `Access to fetch at '...' from origin '...' has been blocked by CORS policy`
   - 対処法: API GatewayのCORS設定を確認し、フロントエンドのオリジン（`http://localhost:3000`など）を許可する

2. **404エラー**:
   - エラーメッセージ: `404 Not Found`
   - 対処法: API GatewayのエンドポイントURLが正しいか確認（ステージ名が含まれているかなど）

3. **500エラー**:
   - エラーメッセージ: `500 Internal Server Error`
   - 対処法: Lambda関数のログ（CloudWatch Logs）を確認し、エラーの原因を特定する

4. **タイムアウトエラー**:
   - エラーメッセージ: `Timeout`または`Request timeout`
   - 対処法: Lambda関数のタイムアウト設定を確認し、必要に応じて延長する（最大15分）

---

## 6. トラブルシューティング

### 6.1 環境変数が読み込まれない

**症状**: `NEXT_PUBLIC_API_BASE_URL`が空文字列になる

**対処法**:
1. `.env.local`ファイルがプロジェクトルートに存在するか確認
2. 環境変数名が正しいか確認（`NEXT_PUBLIC_`プレフィックスが必要）
3. 開発サーバーを再起動する（環境変数の変更は再起動が必要）
4. `.env.local`ファイルの構文エラーがないか確認（コメントや空行は問題ありません）

### 6.2 API GatewayのエンドポイントURLが正しくない

**症状**: 404エラーが発生する

**対処法**:
1. API Gatewayコンソールで、実際のエンドポイントURLを確認
2. `.env.local`の`NEXT_PUBLIC_API_BASE_URL`が正しいか確認
3. HTTP APIとREST APIでURL形式が異なるため、正しい形式を使用する
4. ステージ名が含まれているか確認（REST APIの場合）

### 6.3 CORSエラーが発生する

**症状**: ブラウザのコンソールにCORSエラーが表示される

**対処法**:
1. API GatewayのCORS設定を確認
2. フロントエンドのオリジン（`http://localhost:3000`など）が許可されているか確認
3. CORS設定を変更した場合は、必ずデプロイを実行する
4. プリフライトリクエスト（OPTIONS）が正しく処理されているか確認

### 6.4 Lambda関数がエラーを返す

**症状**: 500エラーが発生する

**対処法**:
1. CloudWatch LogsでLambda関数のログを確認
2. Lambda関数の環境変数が正しく設定されているか確認
3. RDSやDynamoDBへの接続が正常か確認
4. IAMロールの権限が正しく設定されているか確認

### 6.5 レスポンス形式が一致しない

**症状**: フロントエンドでパースエラーが発生する

**対処法**:
1. Lambda関数のレスポンス形式を確認（`backend/common/response.py`）
2. フロントエンドで期待される形式を確認（`lib/api.ts`）
3. エラー時のレスポンス形式が`{ error: { code, message, details } }`になっているか確認
4. 成功時のレスポンス形式がAPIエンドポイントごとに正しいか確認

### 6.6 統合が設定されていない（「有効なルートが存在しない」エラー）

**症状**: 
- API Gatewayのデプロイ時に「Unable to deploy API because no valid routes exist in this API」エラーが発生する
- フロントエンドからAPIを呼び出すと「Failed to fetch」エラーが発生する
- ルートは作成されているが、統合が紐付けられていない

**原因**:
- ルートは作成されているが、統合（Integration）が作成されていない
- または、統合は作成されているが、ルートに紐付けられていない

**確認方法（AWS CLI）**:

```bash
# API IDを取得
API_ID=$(aws apigatewayv2 get-apis --region ap-northeast-1 --query 'Items[?Name==`youtube-dashboard-apis`].ApiId' --output text)

# ルートと統合の紐付けを確認
aws apigatewayv2 get-routes --api-id $API_ID --region ap-northeast-1 --output table --query 'Items[*].[RouteKey,Target]'

# 統合一覧を確認
aws apigatewayv2 get-integrations --api-id $API_ID --region ap-northeast-1 --output json
```

**問題がある状態の例**:
```
+----------------------------+--------+
|  POST /channels/import     |  null  |  ← Targetがnull = 統合が紐付けられていない
|  GET /channels             |  null  |
|  GET /channels/{id}        |  null  |
|  GET /channels/{id}/videos|  null  |
+----------------------------+--------+
```

**正常な状態の例**:
```
+----------------------------+------------------------+
|  POST /channels/import     |  integrations/0c8v8jt  |  ← 統合が紐付けられている
|  GET /channels             |  integrations/p0k201j  |
|  GET /channels/{id}        |  integrations/ynq6pep  |
|  GET /channels/{id}/videos |  integrations/pv7dkv1  |
+----------------------------+------------------------+
```

**対処法（AWS CLI）**:

1. **Lambda関数のARNを取得**:
```bash
# 各Lambda関数のARNを取得
CHANNEL_IMPORT_ARN=$(aws lambda get-function --function-name youtube-dashboard-channel-import --region ap-northeast-1 --query 'Configuration.FunctionArn' --output text)
LIST_CHANNELS_ARN=$(aws lambda get-function --function-name youtube-dashboard-list-channels --region ap-northeast-1 --query 'Configuration.FunctionArn' --output text)
GET_CHANNEL_DETAIL_ARN=$(aws lambda get-function --function-name youtube-dashboard-get-channel-detail --region ap-northeast-1 --query 'Configuration.FunctionArn' --output text)
GET_CHANNEL_VIDEOS_ARN=$(aws lambda get-function --function-name youtube-dashboard-get-channel-videos --region ap-northeast-1 --query 'Configuration.FunctionArn' --output text)
```

2. **統合を作成**:
```bash
# 各Lambda関数に対して統合を作成
INTEGRATION_1=$(aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri $CHANNEL_IMPORT_ARN \
  --payload-format-version "1.0" \
  --region ap-northeast-1 \
  --query 'IntegrationId' --output text)

INTEGRATION_2=$(aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri $LIST_CHANNELS_ARN \
  --payload-format-version "1.0" \
  --region ap-northeast-1 \
  --query 'IntegrationId' --output text)

INTEGRATION_3=$(aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri $GET_CHANNEL_DETAIL_ARN \
  --payload-format-version "1.0" \
  --region ap-northeast-1 \
  --query 'IntegrationId' --output text)

INTEGRATION_4=$(aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri $GET_CHANNEL_VIDEOS_ARN \
  --payload-format-version "1.0" \
  --region ap-northeast-1 \
  --query 'IntegrationId' --output text)
```

3. **ルートIDを取得**:
```bash
# 各ルートのIDを取得
ROUTE_1=$(aws apigatewayv2 get-routes --api-id $API_ID --region ap-northeast-1 --query 'Items[?RouteKey==`POST /channels/import`].RouteId' --output text)
ROUTE_2=$(aws apigatewayv2 get-routes --api-id $API_ID --region ap-northeast-1 --query 'Items[?RouteKey==`GET /channels`].RouteId' --output text)
ROUTE_3=$(aws apigatewayv2 get-routes --api-id $API_ID --region ap-northeast-1 --query 'Items[?RouteKey==`GET /channels/{id}`].RouteId' --output text)
ROUTE_4=$(aws apigatewayv2 get-routes --api-id $API_ID --region ap-northeast-1 --query 'Items[?RouteKey==`GET /channels/{id}/videos`].RouteId' --output text)
```

4. **ルートに統合を紐付け**:
```bash
# 各ルートに統合を紐付け
aws apigatewayv2 update-route --api-id $API_ID --route-id $ROUTE_1 --target "integrations/$INTEGRATION_1" --region ap-northeast-1
aws apigatewayv2 update-route --api-id $API_ID --route-id $ROUTE_2 --target "integrations/$INTEGRATION_2" --region ap-northeast-1
aws apigatewayv2 update-route --api-id $API_ID --route-id $ROUTE_3 --target "integrations/$INTEGRATION_3" --region ap-northeast-1
aws apigatewayv2 update-route --api-id $API_ID --route-id $ROUTE_4 --target "integrations/$INTEGRATION_4" --region ap-northeast-1
```

5. **デプロイ**:
```bash
# デプロイを実行
aws apigatewayv2 create-deployment --api-id $API_ID --stage-name '$default' --region ap-northeast-1
```

**対処法（GUI）**:

1. API Gatewayコンソールで、作成したHTTP APIを選択
2. **統合**タブで、各Lambda関数に対して統合を作成（セクション3.5.5を参照）
3. **ルート**タブで、各ルートに統合を紐付け（セクション3.5.5を参照）
4. **デプロイ**タブで、デプロイを実行

**今回の問題の原因**:
- ルートは作成されていたが、統合が作成されていなかった
- そのため、ルートの`Target`が`null`になり、「有効なルートが存在しない」と判断された
- 統合を作成し、ルートに紐付けることで解決した

**学習ポイント**:
- API Gateway HTTP APIでは、**ルート**と**統合**は別々に作成する必要がある
- ルートだけでは動作せず、統合に紐付けられていないとリクエストを処理できない
- 統合を作成する際は、`PayloadFormatVersion`（HTTP APIでは`1.0`）を指定する必要がある
- ルートと統合を設定した後は、必ずデプロイを実行する必要がある

### 6.7 Lambda関数の環境変数が設定されていない（500エラー）

**症状**: 
- APIを呼び出すと500エラーが発生する
- CloudWatch Logsに「Can't connect to MySQL server on 'localhost'」エラーが表示される
- Lambda関数の環境変数が`null`になっている

**原因**:
- Lambda関数に必要な環境変数（`DB_HOST`、`DB_USER`、`DB_PASSWORD`、`DB_NAME`など）が設定されていない
- 環境変数が`null`の場合、`backend/constants/config.py`で`os.getenv()`が`None`を返し、デフォルト値が`localhost`になっている可能性がある

**確認方法（AWS CLI）**:

```bash
# Lambda関数の環境変数を確認
aws lambda get-function-configuration \
  --function-name youtube-dashboard-list-channels \
  --region ap-northeast-1 \
  --query 'Environment.Variables' \
  --output json

# RDSのエンドポイントを確認
aws rds describe-db-instances \
  --region ap-northeast-1 \
  --query 'DBInstances[?contains(DBInstanceIdentifier, `youtube`)].{Endpoint: Endpoint.Address, Port: Endpoint.Port}' \
  --output table
```

**必要な環境変数**:

| 環境変数名 | 説明 | 取得方法 |
|-----------|------|---------|
| `DB_HOST` | RDSのエンドポイント | RDSコンソールの「接続とセキュリティ」タブから取得 |
| `DB_USER` | RDSのマスターユーザー名 | RDS作成時に設定した値 |
| `DB_PASSWORD` | RDSのマスターパスワード | RDS作成時に設定した値 |
| `DB_NAME` | データベース名 | 通常は`analytics`など |
| `YOUTUBE_API_KEY` | YouTube Data API v3のAPIキー | [詳細な取得方法はこちら](#69-youtube-data-api-v3のapiキー取得方法) |
| `MIN_FETCH_INTERVAL` | 更新間隔（秒） | デフォルト: `600`（10分） |
| `DYNAMODB_TABLE_NAME` | DynamoDBテーブル名 | デフォルト: `channel_update_cache` |


**対処法（AWS CLI）**:

```bash
# RDSのエンドポイントを取得
DB_HOST=$(aws rds describe-db-instances \
  --region ap-northeast-1 \
  --query 'DBInstances[?contains(DBInstanceIdentifier, `youtube`)].Endpoint.Address' \
  --output text)

# すべてのLambda関数に環境変数を設定
for func in youtube-dashboard-channel-import youtube-dashboard-list-channels youtube-dashboard-get-channel-detail youtube-dashboard-get-channel-videos; do
  aws lambda update-function-configuration \
    --function-name $func \
    --region ap-northeast-1 \
    --environment "Variables={
      DB_HOST=$DB_HOST,
      DB_USER=admin,
      DB_PASSWORD=YOUR_PASSWORD,
      DB_NAME=analytics,
      YOUTUBE_API_KEY=YOUR_API_KEY,
      MIN_FETCH_INTERVAL=600,
      DYNAMODB_TABLE_NAME=channel_update_cache
    }"
done
```

**注意**: 
- `YOUR_PASSWORD`と`YOUR_API_KEY`は実際の値に置き換えてください
- パスワードやAPIキーは機密情報のため、AWS Systems Manager Parameter StoreやSecrets Managerの使用を推奨します

**対処法（GUI）**:

1. Lambdaコンソールで、各Lambda関数を選択
2. **設定**タブ → **環境変数**セクションで**編集**をクリック
3. 必要な環境変数を追加（上記の表を参照）
4. **保存**をクリック

**今回の問題の原因**:
- Lambda関数の環境変数が`null`になっていた
- そのため、`DB_HOST`が`None`になり、デフォルトで`localhost`に接続しようとした
- RDSはVPC内にあるため、`localhost`では接続できない

**学習ポイント**:
- Lambda関数は環境変数から設定を読み取るため、環境変数の設定が必須
- RDSに接続する場合は、RDSのエンドポイントを`DB_HOST`に設定する必要がある
- VPC内のRDSに接続する場合は、Lambda関数も同じVPC内に配置する必要がある（VPC設定は既に完了している）

### 6.8 ステージ名がURLに含まれる場合の注意点

**症状**: 
- `.env.local`の`NEXT_PUBLIC_API_BASE_URL`にステージ名（例: `/APIs`）が含まれている
- リクエストURLが`https://{api-id}.execute-api.{region}.amazonaws.com/APIs/channels`のようになる

**説明**:
- API Gateway HTTP APIでは、ステージ名がURLに含まれる場合と含まれない場合がある
- `$default`ステージの場合は、通常URLに含まれない
- カスタムステージ名（例: `APIs`、`prod`、`dev`）を作成した場合は、URLに含まれる

**確認方法**:

```bash
# ステージ一覧を確認
aws apigatewayv2 get-stages \
  --api-id {api-id} \
  --region ap-northeast-1 \
  --output json | jq 'Items[] | {StageName, DeploymentId}'

# ステージの呼び出しURLを確認
aws apigatewayv2 get-stage \
  --api-id {api-id} \
  --stage-name {stage-name} \
  --region ap-northeast-1 \
  --query '{StageName: StageName, ApiEndpoint: "$context.domainName"}' \
  --output json
```

**対処法**:

1. **ステージ名を含める場合**（推奨）:
   - `.env.local`に`NEXT_PUBLIC_API_BASE_URL=https://{api-id}.execute-api.{region}.amazonaws.com/{stage-name}`を設定
   - 例: `NEXT_PUBLIC_API_BASE_URL=https://vwq9v5ap08.execute-api.ap-northeast-1.amazonaws.com/APIs`

2. **ステージ名を含めない場合**:
   - `$default`ステージを使用する
   - `.env.local`に`NEXT_PUBLIC_API_BASE_URL=https://{api-id}.execute-api.{region}.amazonaws.com`を設定
   - 例: `NEXT_PUBLIC_API_BASE_URL=https://vwq9v5ap08.execute-api.ap-northeast-1.amazonaws.com`

**注意**:
- ステージ名を変更した場合は、`.env.local`も更新する必要がある
- 開発サーバーを再起動する必要がある

### 6.9 YouTube Data API v3のAPIキー取得方法

**概要**:
- YouTube Data API v3を使用して、公開されているチャンネルや動画の情報を取得できます
- 自分が所有していないチャンネルからも情報を取得可能です（チャンネルが公開されている場合）
- APIキーだけで取得可能で、OAuth認証は不要です

**手順**:

#### ステップ1: Google Cloud Consoleにアクセス

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. Googleアカウントでログイン（GmailアカウントでOK）

#### ステップ2: プロジェクトの作成（初回のみ）

1. 画面上部の**プロジェクト選択**をクリック
2. **新しいプロジェクト**をクリック
3. プロジェクト名を入力（例: `youtube-dashboard`）
4. **作成**をクリック
5. プロジェクトが作成されるまで数秒待つ（通知バーで確認可能）

#### ステップ3: YouTube Data API v3を有効化

1. 左側のメニューから**APIとサービス** → **ライブラリ**を選択
2. 検索ボックスに「YouTube Data API v3」と入力
3. **YouTube Data API v3**を選択
4. **有効にする**ボタンをクリック
5. 有効化が完了するまで数秒待つ

**注意**: 初回は利用規約への同意を求められる場合があります

#### ステップ4: APIキーの作成

1. 左側のメニューから**APIとサービス** → **認証情報**を選択
2. 画面上部の**認証情報を作成** → **APIキー**をクリック
3. APIキーが作成され、ポップアップが表示されます
4. **APIキーをコピー**をクリックして、APIキーをコピー
   - **重要**: このAPIキーは後で確認できないため、必ずコピーして安全な場所に保存してください

#### ステップ5: APIキーの制限を設定（推奨）

セキュリティのため、APIキーに制限を設定することを推奨します：

1. 作成したAPIキーの**編集**（鉛筆アイコン）をクリック
2. **APIキーの制限**セクションで：
   - **アプリケーションの制限**: **HTTPリファラー（ウェブサイト）**を選択
     - 本番環境の場合は、特定のドメインを追加（例: `https://yourdomain.com/*`）
     - 開発環境の場合は、`http://localhost:*`を追加
   - **APIの制限**: **特定のAPIを制限**を選択
     - **YouTube Data API v3**のみを選択
3. **保存**をクリック

**注意**: 
- 制限を設定すると、指定した条件以外ではAPIキーが使用できなくなります
- 開発中は制限を緩く設定し、本番環境では厳しく設定することを推奨します

#### ステップ6: APIキーをLambda関数の環境変数に設定

**方法1: AWS CLIで設定**

```bash
# すべてのLambda関数に環境変数を設定
for func in youtube-dashboard-channel-import youtube-dashboard-list-channels youtube-dashboard-get-channel-detail youtube-dashboard-get-channel-videos; do
  aws lambda update-function-configuration \
    --function-name $func \
    --region ap-northeast-1 \
    --environment "Variables={
      YOUTUBE_API_KEY=YOUR_API_KEY_HERE
    }"
done
```

**方法2: AWSコンソールで設定**

1. Lambdaコンソールで、各Lambda関数を選択
2. **設定**タブ → **環境変数**セクションで**編集**をクリック
3. **環境変数を追加**をクリック
4. **キー**: `YOUTUBE_API_KEY`、**値**: コピーしたAPIキーを貼り付け
5. **保存**をクリック

#### ステップ7: APIキーの動作確認（オプション）

APIキーが正しく動作するか確認するには、以下のコマンドを実行：

```bash
# テスト用のチャンネルID（例: Google公式チャンネル）
CHANNEL_ID="UC_x5XG1OV2P6uZZ5FSM9Ttw"
API_KEY="YOUR_API_KEY_HERE"

curl "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id=${CHANNEL_ID}&key=${API_KEY}"
```

正常に動作する場合、JSON形式でチャンネル情報が返ってきます。

**APIキーの利用制限**:

- **無料枠**: 1日あたり10,000ユニット
- **クォータ消費**:
  - `channels.list`: 1リクエスト = 1ユニット
  - `videos.list`: 1リクエスト = 1ユニット
  - `playlistItems.list`: 1リクエスト = 1ユニット
- **クォータ超過**: 1日あたり10,000ユニットを超えると、その日の残り時間はAPIが使用できなくなります
- **有料プラン**: 必要に応じて、Google Cloud Consoleでクォータの増加を申請できます

**トラブルシューティング**:

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `API key not valid` | APIキーが無効 | APIキーを再確認し、正しくコピーしたか確認 |
| `API key not found` | APIキーが存在しない | Google Cloud ConsoleでAPIキーが作成されているか確認 |
| `API has not been used` | YouTube Data API v3が有効化されていない | Google Cloud ConsoleでYouTube Data API v3を有効化 |
| `Quota exceeded` | 1日のクォータを超過 | 翌日まで待つか、有料プランにアップグレード |
| `Access Not Configured` | APIが有効化されていない | Google Cloud ConsoleでYouTube Data API v3を有効化 |

**参考リンク**:
- [YouTube Data API v3 ドキュメント](https://developers.google.com/youtube/v3)
- [Google Cloud Console](https://console.cloud.google.com/)
- [APIキーの作成と管理](https://cloud.google.com/docs/authentication/api-keys)

### 6.10 Lambda関数のリソースベースポリシーが設定されていない（500エラー）

**症状**: 
- API Gateway経由でリクエストを送ると500エラーが発生する
- エラーメッセージ: `{"message":"Internal Server Error"}`
- Lambda関数を直接呼び出すと正常に動作する
- Lambda関数のログには最新のリクエストが記録されていない（API GatewayがLambda関数を呼び出せていない）

**原因**:
- Lambda関数にリソースベースのポリシーが設定されていない
- API GatewayがLambda関数を呼び出す権限がない
- その結果、API GatewayがLambda関数を呼び出せず、500エラーが返される

**確認方法（AWS CLI）**:

```bash
# Lambda関数のリソースベースポリシーを確認
aws lambda get-policy \
  --function-name youtube-dashboard-list-channels \
  --region ap-northeast-1 \
  --output json
```

**エラーメッセージ**: `ResourceNotFoundException: The resource you requested does not exist` が返ってきた場合、ポリシーが設定されていません。

**対処法（GUI）**:

#### 方法1: Lambdaコンソールから設定（推奨）

1. **Lambdaコンソールにアクセス**:
   - AWSコンソールで**Lambda**サービスを開く
   - https://console.aws.amazon.com/lambda/

2. **Lambda関数を選択**:
   - 左側のメニューから**関数**を選択
   - 対象のLambda関数を選択（例: `youtube-dashboard-list-channels`）

3. **設定タブを開く**:
   - **設定**タブをクリック
   - 左側のメニューから**アクセス権限**を選択

4. **リソースベースポリシーを確認**:
   - **リソースベースポリシー**セクションを確認
   - API Gatewayからの呼び出しを許可するポリシーが存在するか確認

5. **ポリシーが存在しない場合、追加する**:
   - **ポリシーを追加**ボタンをクリック
   - **プリンシパル**に`apigateway.amazonaws.com`を入力
   - **アクション**に`lambda:InvokeFunction`を選択
   - **ソースARN**に以下を入力（`{api-id}`と`{region}`を実際の値に置き換える）:
     ```
     arn:aws:execute-api:{region}:{account-id}:{api-id}/*/*
     ```
   - 例: `arn:aws:execute-api:ap-northeast-1:457553343831:vwq9v5ap08/*/*`
   - **追加**をクリック

6. **すべてのLambda関数に同様の設定を適用**:
   - `youtube-dashboard-channel-import`
   - `youtube-dashboard-list-channels`
   - `youtube-dashboard-get-channel-detail`
   - `youtube-dashboard-get-channel-videos`

#### 方法2: API Gatewayコンソールから設定

1. **API Gatewayコンソールにアクセス**:
   - AWSコンソールで**API Gateway**サービスを開く
   - https://console.aws.amazon.com/apigateway/

2. **HTTP APIを選択**:
   - 左側のメニューから**HTTP API**を選択
   - 対象のAPIを選択

3. **統合を確認**:
   - **統合**タブを開く
   - 各統合（例: `GET /channels`）を選択
   - **統合の詳細**で、Lambda関数が正しく設定されているか確認

4. **Lambda関数の権限を確認**:
   - 統合の詳細画面で、**Lambda関数の権限**セクションを確認
   - **権限を追加**ボタンが表示されている場合、クリックして権限を追加
   - これにより、API GatewayがLambda関数を呼び出す権限が自動的に追加されます

**対処法（AWS CLI）**:

```bash
# API IDを設定
API_ID="vwq9v5ap08"
REGION="ap-northeast-1"
ACCOUNT_ID="457553343831"  # 実際のアカウントIDに置き換える

# ソースARNを構築
SOURCE_ARN="arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/*"

# すべてのLambda関数にリソースベースポリシーを追加
for func in youtube-dashboard-channel-import youtube-dashboard-list-channels youtube-dashboard-get-channel-detail youtube-dashboard-get-channel-videos; do
  aws lambda add-permission \
    --function-name $func \
    --region $REGION \
    --statement-id "apigateway-invoke-$(date +%s)" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "$SOURCE_ARN"
done
```

**確認方法**:

1. **Lambda関数のポリシーを確認**:
   ```bash
   aws lambda get-policy \
     --function-name youtube-dashboard-list-channels \
     --region ap-northeast-1 \
     --output json | jq -r '.Policy' | jq .
   ```

2. **API Gateway経由でリクエストを送信**:
   ```bash
   curl -X GET "https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/channels?limit=5" \
     -H "Content-Type: application/json"
   ```

3. **正常なレスポンスが返ってくることを確認**:
   - ステータスコード: `200`
   - レスポンスボディ: `{"items": [...], "totalCount": ...}`

**今回の問題の原因**:
- Lambda関数にリソースベースのポリシーが設定されていなかった
- API GatewayがLambda関数を呼び出す権限がなかった
- その結果、API GatewayがLambda関数を呼び出せず、500エラーが返されていた
- Lambda関数を直接呼び出すと正常に動作していたため、Lambda関数自体には問題がなかった

**学習ポイント**:
- API Gateway HTTP APIでLambda関数を統合する場合、Lambda関数にリソースベースのポリシーが必要
- リソースベースのポリシーにより、API GatewayがLambda関数を呼び出す権限が付与される
- ポリシーが設定されていない場合、API GatewayはLambda関数を呼び出せず、500エラーが返される
- Lambda関数を直接呼び出すと正常に動作する場合、リソースベースのポリシーの問題である可能性が高い

**参考リンク**:
- [Lambda関数のリソースベースポリシー](https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/access-control-resource-based.html)
- [API GatewayとLambda関数の統合](https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html)

### 6.11 API Gatewayから200 OKが返ってくるのにフロントエンドでエラーが表示される

**症状**: 
- API Gateway経由でリクエストを送ると200 OKが返ってくる
- レスポンスも正しい（例: `{"items": [], "totalCount": 0}`）
- CORSヘッダーも設定されている
- しかし、フロントエンドでエラーメッセージが表示される
- エラーメッセージ: "APIサーバーに接続できません。"

**原因**:
- `.env.local`ファイルが存在しない、または環境変数が正しく読み込まれていない
- 開発サーバーが再起動されていない（環境変数の変更は再起動が必要）
- ブラウザのコンソールで実際のエラーが発生している（CORSエラー、JSONパースエラーなど）
- レスポンスのパースに失敗している

**確認方法（GUI）**:

1. **`.env.local`ファイルの確認**:
   - プロジェクトルートに`.env.local`ファイルが存在するか確認
   - ファイルが存在する場合、内容を確認：
     ```
     NEXT_PUBLIC_API_BASE_URL=https://{api-id}.execute-api.{region}.amazonaws.com/{stage}
     ```
   - 例: `NEXT_PUBLIC_API_BASE_URL=https://vwq9v5ap08.execute-api.ap-northeast-1.amazonaws.com/APIs`

2. **ブラウザの開発者ツールで確認**:
   - 開発者ツール（F12）を開く
   - **コンソール**タブでエラーメッセージを確認
   - **ネットワーク**タブでリクエストとレスポンスを確認：
     - リクエストURLが正しいか
     - ステータスコードが200か
     - レスポンスボディが正しい形式か
     - CORSエラーが発生していないか

3. **開発サーバーの再起動**:
   - 開発サーバーを停止（Ctrl+C）
   - 再度起動: `npm run dev`
   - 環境変数の変更は再起動が必要

**対処法（GUI）**:

#### 方法1: `.env.local`ファイルを作成・確認

1. **プロジェクトルートに`.env.local`ファイルを作成**:
   - プロジェクトルート（`youtube-dashboard/`）に`.env.local`ファイルを作成
   - 以下の内容を記述：
     ```
     NEXT_PUBLIC_API_BASE_URL=https://{api-id}.execute-api.{region}.amazonaws.com/{stage}
     ```
   - 例: `NEXT_PUBLIC_API_BASE_URL=https://vwq9v5ap08.execute-api.ap-northeast-1.amazonaws.com/APIs`

2. **開発サーバーを再起動**:
   - 開発サーバーを停止（Ctrl+C）
   - 再度起動: `npm run dev`

#### 方法2: ブラウザのコンソールでエラーを確認

1. **開発者ツールを開く**:
   - ブラウザでF12キーを押す
   - **コンソール**タブを開く

2. **エラーメッセージを確認**:
   - エラーメッセージの詳細を確認
   - よくあるエラー：
     - `Failed to fetch`: CORSエラーまたはネットワークエラー
     - `JSONパースエラー`: レスポンスの形式が正しくない
     - `レスポンスが空です`: レスポンスボディが空

3. **ネットワークタブで確認**:
   - **ネットワーク**タブを開く
   - リクエストを選択
   - **ヘッダー**タブでリクエストヘッダーとレスポンスヘッダーを確認
   - **プレビュー**タブでレスポンスボディを確認

#### 方法3: API GatewayのCORS設定を確認

1. **API Gatewayコンソールにアクセス**:
   - AWSコンソールで**API Gateway**サービスを開く
   - https://console.aws.amazon.com/apigateway/

2. **HTTP APIを選択**:
   - 左側のメニューから**HTTP API**を選択
   - 対象のAPIを選択

3. **CORS設定を確認**:
   - **CORS**セクションを開く
   - **アクセス制御許可オリジン**に`http://localhost:3000`が含まれているか確認
   - 含まれていない場合、追加する

4. **CORS設定をデプロイ**:
   - CORS設定を変更した場合は、**デプロイ**をクリック
   - **ステージ**: `APIs`（または作成したステージ）を選択
   - **デプロイ**をクリック

**対処法（AWS CLI）**:

```bash
# .env.localファイルの内容を確認
cat .env.local

# 環境変数が正しく設定されているか確認（Next.jsのビルド時）
node -e "console.log(process.env.NEXT_PUBLIC_API_BASE_URL || '(未設定)')"

# API GatewayのCORS設定を確認
aws apigatewayv2 get-api \
  --api-id vwq9v5ap08 \
  --region ap-northeast-1 \
  --query 'CorsConfiguration' \
  --output json

# CORS設定を更新（必要に応じて）
aws apigatewayv2 update-api \
  --api-id vwq9v5ap08 \
  --region ap-northeast-1 \
  --cors-configuration '{
    "AllowCredentials": false,
    "AllowHeaders": ["authorization", "content-type"],
    "AllowMethods": ["GET", "POST", "OPTIONS"],
    "AllowOrigins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    "MaxAge": 300
  }'

# API Gatewayをデプロイ
aws apigatewayv2 create-deployment \
  --api-id vwq9v5ap08 \
  --region ap-northeast-1 \
  --stage-name APIs
```

**確認方法**:

1. **ブラウザのコンソールでエラーを確認**:
   - 開発者ツール（F12）のコンソールタブを開く
   - エラーメッセージの詳細を確認
   - 改善したエラーハンドリングにより、詳細なエラーメッセージが表示される

2. **ネットワークタブでリクエストを確認**:
   - 開発者ツール（F12）のネットワークタブを開く
   - リクエストを選択
   - ステータスコード、レスポンスヘッダー、レスポンスボディを確認

3. **API Gateway経由でリクエストを送信**:
   ```bash
   curl -X GET "https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/channels?limit=5" \
     -H "Content-Type: application/json" \
     -H "Origin: http://localhost:3000"
   ```

**今回の問題の原因**:
- `.env.local`ファイルが存在しない、または環境変数が正しく読み込まれていない可能性
- 開発サーバーが再起動されていない（環境変数の変更は再起動が必要）
- ブラウザのコンソールで実際のエラーが発生している可能性（CORSエラー、JSONパースエラーなど）

**学習ポイント**:
- Next.jsでは、環境変数の変更は開発サーバーの再起動が必要
- `.env.local`ファイルは`.gitignore`に含まれているため、Gitにコミットされない
- ブラウザの開発者ツールで実際のエラーを確認することが重要
- API Gatewayから200 OKが返ってきても、フロントエンドでエラーが発生する場合がある
- エラーハンドリングを改善することで、より詳細なエラーメッセージが表示される

**参考リンク**:
- [Next.js Environment Variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables)
- [API Gateway HTTP API CORS](https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/http-api-cors.html)

---

## 7. 次のステップ

接続が完了したら、以下の作業を進めてください：

1. **動作確認**: すべてのAPIエンドポイントが正常に動作するか確認
2. **エラーハンドリング**: エラー時の表示を確認し、必要に応じて改善
3. **パフォーマンス**: API呼び出しのパフォーマンスを確認し、必要に応じて最適化
4. **セキュリティ**: 本番環境では、CORS設定を適切に制限する
5. **モニタリング**: CloudWatch LogsでLambda関数のログを監視する

---

## 8. 参考資料

- [AWS_SETUP_GUIDE.md](../backend/AWS_SETUP_GUIDE.md): AWSリソースの設定手順
- [api-error-contract.md](./api-error-contract.md): APIエラーレスポンスの形式
- [plan.md](./plan.md): フロントエンドの仕様書
- [Next.js Environment Variables](https://nextjs.org/docs/app/building-your-application/configuring/environment-variables): Next.jsの環境変数設定

---

## 9. チェックリスト

接続作業を完了するために、以下のチェックリストを確認してください：

- [ ] API GatewayのエンドポイントURLを取得
- [ ] `.env.local`ファイルを作成し、`NEXT_PUBLIC_API_BASE_URL`を設定
- [ ] API Gatewayの統合（Integration）を作成（4つすべて）
- [ ] API Gatewayのルート（Route）を作成し、統合に紐付け（4つすべて）
- [ ] Lambda関数にリソースベースポリシーを設定（API Gatewayからの呼び出しを許可）
- [ ] API Gatewayをデプロイ
- [ ] API GatewayのCORS設定を確認・設定
- [ ] CORS設定をデプロイ
- [ ] Lambda関数のレスポンス形式を確認
- [ ] 開発サーバーを起動
- [ ] ブラウザで動作確認
- [ ] ブラウザの開発者ツールでネットワークリクエストを確認
- [ ] エラーが発生した場合は、トラブルシューティングを実施
- [ ] すべてのAPIエンドポイントが正常に動作することを確認

---

以上で、フロントエンドとバックエンドの接続手順は完了です。


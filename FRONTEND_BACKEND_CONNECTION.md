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


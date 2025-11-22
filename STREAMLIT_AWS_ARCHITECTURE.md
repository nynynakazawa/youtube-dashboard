# StreamlitアプリのAWSアーキテクチャ詳細解説

## 目次

1. [ECS FargateとEC2の違い](#ecs-fargateとec2の違い)
2. [Streamlitアプリのアーキテクチャ](#streamlitアプリのアーキテクチャ)
3. [Lambdaとの関係](#lambdaとの関係)
4. [データベース接続（RDSとDynamoDB）](#データベース接続rdsとdynamodb)
5. [API Gatewayの使用有無](#api-gatewayの使用有無)
6. [全体アーキテクチャ図](#全体アーキテクチャ図)

---

## ECS FargateとEC2の違い

### 基本的な違い

| 項目 | EC2 | ECS Fargate |
|------|-----|-------------|
| **管理レベル** | サーバー（OS）を自分で管理 | コンテナのみ管理（サーバー管理不要） |
| **起動方法** | EC2インスタンスを起動 | コンテナタスクを起動 |
| **スケーリング** | 手動でインスタンス数を調整 | 自動スケーリング対応 |
| **コスト** | インスタンスが起動している間は課金 | タスクが実行されている間だけ課金 |
| **設定の複雑さ** | シンプル（サーバー1台） | やや複雑（クラスター、タスク定義など） |
| **用途** | 開発環境、小規模運用 | 本番環境、大規模運用 |

### EC2の詳細

**EC2とは**:
- 仮想サーバー（Virtual Machine）
- OS（Linux/Windows）を自分で管理
- サーバーに直接SSH接続して操作可能
- アプリケーション、ミドルウェア、OSすべてを自分で管理

**EC2でのStreamlit実行**:
```
[ユーザー] → [EC2インスタンス（Linux）]
              ├─ Python 3.11
              ├─ Streamlit
              └─ アプリケーションコード
              ↓
          [RDS]（直接接続）
```

**自分でサーバーの中身を書く？**
- **いいえ、書く必要はありません**
- Streamlitは既存のフレームワークなので、アプリケーションコード（`app.py`）を書くだけ
- サーバーの設定（OS、Python、依存関係のインストール）は必要ですが、これは一度だけの作業

**EC2での実装手順**:
1. EC2インスタンスを作成（Amazon Linux 2など）
2. Pythonと依存関係をインストール
   ```bash
   sudo yum install python3 pip
   pip3 install streamlit plotly pandas pymysql
   ```
3. Streamlitアプリを配置
4. Streamlitを起動
   ```bash
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

### ECS Fargateの詳細

**ECS Fargateとは**:
- サーバーレスなコンテナ実行環境
- サーバー（EC2）を管理する必要がない
- Dockerコンテナを実行するだけ
- AWSがサーバーの管理、スケーリング、メンテナンスを自動で行う

**ECS FargateでのStreamlit実行**:
```
[ユーザー] → [Application Load Balancer] → [ECS Fargate]
                                                    ├─ Dockerコンテナ
                                                    ├─ Python 3.11
                                                    ├─ Streamlit
                                                    └─ アプリケーションコード
                                                    ↓
                                                [RDS]（直接接続）
```

**自分でサーバーの中身を書く？**
- **いいえ、書く必要はありません**
- Dockerコンテナイメージを作成するだけ
- サーバーの管理はAWSが自動で行う

**ECS Fargateでの実装手順**:
1. Dockerfileを作成
2. Dockerイメージをビルド
3. ECR（Elastic Container Registry）にプッシュ
4. ECSクラスターとタスク定義を作成
5. Fargateでタスクを実行

---

## Streamlitアプリのアーキテクチャ

### Lambdaとは別ルートで処理

**重要**: Streamlitアプリは**Lambdaとは完全に別のアプリケーション**です。

```
┌─────────────────────────────────────────────────────────┐
│                   現在のプロジェクト構成                  │
└─────────────────────────────────────────────────────────┘

[フロントエンド: Next.js]
  │
  ├─→ [API Gateway] → [Lambda関数] → [RDS] / [DynamoDB]
  │      (REST API)
  │
  └─→ [Streamlitアプリ] → [RDS]（直接接続）
        (別のアプリケーション)
```

### 処理フローの違い

#### Lambda関数（既存のREST API）

```
1. フロントエンドからリクエスト
   ↓
2. API Gatewayがリクエストを受信
   ↓
3. Lambda関数を呼び出し（イベント駆動）
   ↓
4. Lambda関数が処理を実行（数秒）
   ↓
5. レスポンスを返す
   ↓
6. Lambda関数は終了
```

**特徴**:
- リクエスト/レスポンス型
- 短時間の処理（数秒〜数分）
- ステートレス（状態を保持しない）
- イベント駆動（リクエストがあるたびに起動）

#### Streamlitアプリ

```
1. ユーザーがブラウザでStreamlitアプリにアクセス
   ↓
2. Streamlitサーバーが常時起動（WebSocket接続）
   ↓
3. ユーザーの操作（ボタンクリック、入力変更など）
   ↓
4. Streamlitサーバーが処理を実行
   ↓
5. リアルタイムでUIを更新（WebSocket経由）
   ↓
6. Streamlitサーバーは継続的に実行
```

**特徴**:
- 常時起動型のWebアプリケーション
- 長時間実行（サーバーが起動している限り）
- ステートフル（セッション状態を保持）
- WebSocketを使用（リアルタイム更新）

### なぜ別ルートなのか？

1. **アーキテクチャの違い**
   - Lambda: イベント駆動、短時間実行
   - Streamlit: 常時起動、長時間実行

2. **用途の違い**
   - Lambda: REST API（データの取得・更新）
   - Streamlit: データ分析ダッシュボード（可視化・分析）

3. **技術的な制約**
   - LambdaではWebSocketとステート管理が困難
   - StreamlitはLambdaの制約と適合しない

---

## データベース接続（RDSとDynamoDB）

### RDSへの接続

**StreamlitアプリはRDSに直接接続します。**

```
[Streamlitアプリ] → [RDS]（直接接続）
  ├─ pymysqlを使用
  ├─ VPC内からのアクセス
  └─ 既存のdb/rds.pyを再利用可能
```

**接続方法**:
- 既存の`backend/db/rds.py`の`get_db_connection()`を再利用
- RDSのエンドポイント、ユーザー名、パスワードを使用
- VPC内からのアクセスが必要（セキュリティグループで許可）

**コード例**:
```python
# backend/streamlit/app.py
from db.rds import get_db_connection

with get_db_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM channels")
        channels = cursor.fetchall()
```

### DynamoDBへの接続

**StreamlitアプリはDynamoDBには接続しません。**

**理由**:
- DynamoDBはLambda関数でのみ使用（キャッシュ制御用）
- Streamlitアプリは分析用で、キャッシュ制御は不要
- RDSから直接データを取得する

**DynamoDBの用途（Lambda関数でのみ使用）**:
```
[Lambda関数: channel_import]
  ├─ DynamoDB: 更新間隔チェック（MIN_FETCH_INTERVAL）
  └─ RDS: データの保存・取得
```

**Streamlitアプリのデータ取得**:
```
[Streamlitアプリ]
  └─ RDS: 分析用データを直接取得
    ├─ channelsテーブル
    ├─ videosテーブル
    └─ video_stats_historyテーブル
```

---

## API Gatewayの使用有無

### StreamlitアプリはAPI Gatewayを使いません

**理由**:
- Streamlitは独自のWebサーバーを持っている
- HTTPリクエストを直接受け取る
- API GatewayはREST API用（Lambda関数用）

### アクセス方法

#### 開発環境（EC2）

```
[ユーザー] → [EC2インスタンス:ポート8501] → [Streamlitアプリ]
```

**設定**:
- EC2のセキュリティグループでポート8501を開放
- パブリックIPまたはドメインでアクセス
- `http://<EC2のパブリックIP>:8501`

#### 本番環境（ECS Fargate）

```
[ユーザー] → [Application Load Balancer] → [ECS Fargate:ポート8501] → [Streamlitアプリ]
```

**設定**:
- Application Load Balancer（ALB）を設定
- ALBがリクエストをFargateタスクに転送
- HTTPS対応（ACMで証明書を取得）

### API Gatewayを使わない場合の代替手段

1. **Application Load Balancer（ALB）**（推奨）
   - HTTPS対応
   - ヘルスチェック
   - 自動スケーリング対応

2. **直接アクセス**（開発環境のみ）
   - EC2のパブリックIPで直接アクセス
   - セキュリティグループでポートを開放

3. **CloudFront**（オプション）
   - CDNとして使用
   - ALBの前に配置してキャッシュ

---

## 全体アーキテクチャ図

### 現在のプロジェクト全体像

```
┌─────────────────────────────────────────────────────────────────┐
│                      YouTube Dashboard プロジェクト                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 1. フロントエンド（Next.js）                                      │
│    - チャンネル登録、一覧表示、動画一覧                          │
│    - 簡易グラフ表示                                              │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ├─────────────────┐
                          │                 │
                          ▼                 ▼
┌─────────────────────────────────┐  ┌─────────────────────────────┐
│ 2. REST API（Lambda関数）        │  │ 3. 分析ダッシュボード        │
│    - API Gateway                │  │    - Streamlitアプリ         │
│    - Lambda関数                 │  │    - EC2/ECS Fargate        │
│      ├─ channel_import         │  │    - 直接RDS接続             │
│      ├─ list_channels          │  │    - データ分析・可視化       │
│      ├─ get_channel_detail     │  │                              │
│      └─ get_channel_videos     │  │                              │
└─────────────────────────────────┘  └─────────────────────────────┘
         │                                      │
         ├──────────────┬──────────────┐       │
         │              │              │       │
         ▼              ▼              ▼       ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 4. RDS      │  │ 5. DynamoDB │  │ 4. RDS      │
│ (MySQL)     │  │ (キャッシュ) │  │ (MySQL)     │
│             │  │             │  │             │
│ - channels  │  │ - 更新間隔   │  │ - channels  │
│ - videos    │  │   チェック    │  │ - videos    │
│ - stats     │  │             │  │ - stats     │
└─────────────┘  └─────────────┘  └─────────────┘
```

### データフロー

#### REST API（Lambda関数）のデータフロー

```
[フロントエンド]
  ↓ HTTPリクエスト: POST /channels/import
[API Gateway]
  ↓ イベント
[Lambda関数: channel_import]
  ├─ DynamoDB: 更新間隔チェック
  ├─ YouTube Data API: データ取得
  ├─ RDS: データ保存
  └─ DynamoDB: キャッシュ更新
  ↓ レスポンス
[API Gateway]
  ↓ HTTPレスポンス
[フロントエンド]
```

#### Streamlitアプリのデータフロー

```
[ユーザーのブラウザ]
  ↓ WebSocket接続
[Streamlitサーバー（EC2/ECS Fargate）]
  ↓ SQLクエリ
[RDS]
  ↓ データ取得
[Streamlitサーバー]
  ├─ データ処理・集計
  ├─ グラフ生成（Plotly）
  └─ UI更新
  ↓ WebSocket経由でリアルタイム更新
[ユーザーのブラウザ]
```

---

## まとめ

### ECS FargateとEC2の違い

- **EC2**: サーバーを自分で管理、シンプル、開発環境向け
- **ECS Fargate**: サーバー管理不要、自動スケーリング、本番環境向け

### Streamlitアプリの特徴

- **Lambdaとは別ルート**: 完全に独立したアプリケーション
- **自分でサーバーの中身を書く必要はない**: Streamlitフレームワークを使用
- **RDSに直接接続**: 既存の`db/rds.py`を再利用
- **DynamoDBには接続しない**: Lambda関数でのみ使用

### API Gatewayの使用

- **StreamlitアプリはAPI Gatewayを使わない**
- **代替手段**: Application Load Balancer（ALB）または直接アクセス

### 推奨構成

- **開発環境**: EC2でStreamlitアプリを実行
- **本番環境**: ECS FargateでStreamlitアプリを実行
- **データ取得**: RDSに直接接続（既存のコードを再利用）


# AWS設定手順書（GUI操作）

このドキュメントでは、YouTube DashboardのバックエンドをAWS上に構築するための手順をGUI操作で説明します。

## 前提条件

- AWSアカウントを持っていること
- YouTube Data API v3のAPIキーを取得済みであること

---

## 0. データベースエンジンの選択について

### なぜMySQLを選択するのか？

AWS RDSでは以下のデータベースエンジンが利用可能です：

- **Aurora (MySQL Compatible)** - AWSが提供するMySQL互換のマネージドデータベース
- **Aurora (PostgreSQL Compatible)** - AWSが提供するPostgreSQL互換のマネージドデータベース
- **MySQL** - オープンソースのリレーショナルデータベース
- **PostgreSQL** - オープンソースのリレーショナルデータベース
- **MariaDB** - MySQLからフォークしたオープンソースデータベース
- **Oracle** - 商用データベース（ライセンス費用が高い）
- **Microsoft SQL Server** - Microsoftの商用データベース（ライセンス費用が高い）

これらはすべてRDBMS（リレーショナルデータベース管理システム）ですが、それぞれに特徴があります。

#### 各エンジンの特徴と違い

| エンジン | 特徴 | コスト | 用途 |
|---------|------|--------|------|
| **Aurora MySQL** | AWS最適化、自動スケーリング、高可用性、読み取りレプリカが高速 | 高め（高性能） | 大規模な本番環境、高トラフィック |
| **Aurora PostgreSQL** | PostgreSQL互換、Auroraの高性能機能 | 高め（高性能） | PostgreSQLが必要な大規模環境 |
| **MySQL** | シンプル、軽量、無料、広く使われている | 低め | 小〜中規模のアプリケーション |
| **PostgreSQL** | 高度な機能、JSONサポートが強い、標準SQL準拠 | 低め | 複雑なクエリが必要なアプリケーション |
| **MariaDB** | MySQL互換、コミュニティ主導 | 低め | MySQLの代替として |
| **Oracle** | エンタープライズ向け、高機能 | 非常に高い | 大企業の基幹システム |
| **SQL Server** | Windows環境に最適、Microsoftエコシステム | 高い | Windowsベースのエンタープライズ |

#### このプロジェクトでMySQLを選択する理由

1. **コスト効率**: 無料利用枠（`db.t3.micro`）が利用可能で、開発・小規模運用に適している
2. **シンプルさ**: このプロジェクトの要件（チャンネル情報、動画情報、統計履歴の保存）には十分な機能を提供
3. **互換性**: プロジェクトで使用している`pymysql`ライブラリとの親和性が高い
4. **学習コスト**: 広く使われており、ドキュメントやコミュニティサポートが豊富
5. **スキーマ設計**: 既存のスキーマ（`schema.sql`）がMySQLの構文（`AUTO_INCREMENT`、`ON UPDATE CURRENT_TIMESTAMP`など）を使用している

#### 他のエンジンを選択する場合の考慮点

- **Aurora MySQL**: 将来的にトラフィックが増加し、自動スケーリングや高可用性が必要になった場合
- **PostgreSQL**: JSON型の高度な操作や、より複雑なクエリが必要になった場合
- **MariaDB**: MySQLとほぼ互換だが、コミュニティ主導の開発を重視する場合

現時点では、**MySQL**がこのプロジェクトの要件とコストバランスに最も適しています。

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
   - **EC2接続をセットアップする**: **チェックしない（任意）**
     - このオプションは、RDSに接続するためのEC2インスタンス（Bastion Host）を自動的に作成するものです
     - **このプロジェクトでは不要です**。理由：
       - Lambda関数から直接RDS Proxy経由で接続するため
       - スキーマの初期化はローカル環境から行うか、後述の方法で行います
     - EC2接続が必要な場合：
       - データベースの直接操作やデバッグが必要な場合
       - ローカル環境からVPC内のRDSに接続できない場合
       - その場合は、手動でEC2インスタンスを作成して接続することも可能です
   - **マルチAZ**: **なし**（開発環境の場合）
     - 本番環境では可用性向上のため「あり」を推奨しますが、コストが約2倍になります
   - **サブネットグループ**: 新しいDBサブネットグループの作成でOK
   - **自動バックアップ**: **有効**（推奨）
     - **無料枠を使用する場合**: **バックアップ保持期間を1日に設定**（重要）
       - 無料枠ではバックアップ保持期間が最大1日に制限されています
       - デフォルトでは7日間などに設定されている場合があるため、必ず1日に変更してください
       - 設定画面の「バックアップ」セクションで「バックアップ保持期間」を1日に設定
     - 本番環境では7日間以上を推奨しますが、無料枠では1日のみ可能です
   - **VPCセキュリティグループ**: **defaultは避ける**（重要）
     - セキュリティ上、専用のセキュリティグループを作成することを推奨します
     - 後でセキュリティグループを変更することも可能ですが、作成時に設定する方が安全です
     - セクション7でセキュリティグループの設定方法を説明しています
   - **パブリックアクセス可能**: **なし**（正しい設定）
   - **データベースポート**: `3306`（MySQLのデフォルトポート、問題なし）
   - **モニタリングタイプ**: **データベースインサイト - スタンダード**は有料の可能性があります
     - 開発環境では「拡張モニタリング」または「モニタリングなし」でも問題ありません
     - CloudWatch Logsは無料枠があるため、基本的なモニタリングには十分です
   - **パフォーマンスインサイト**: 有効になっていなくても問題なし（必要に応じて後から有効化可能）
   - **モニタリング**: 有効でOK（CloudWatch Logsは無料枠あり）
   - **メンテナンス**: マイナーバージョン自動アップグレードが有効でOK
   - **削除保護**: 開発環境では有効になっていなくても問題なし
     - 本番環境では誤削除を防ぐため有効化を推奨します
   - **暗号化**: **有効**（推奨、セキュリティ上重要）
   - **VPC**: Default VPCで問題なし（開発環境の場合）
     - 本番環境では専用VPCの作成を推奨します
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

## 1.5 RDS推奨アドオンについて

RDS作成後、AWSコンソールでは以下の推奨アドオンが表示される場合があります。それぞれの説明と、このプロジェクトでの必要性を説明します。

### ElastiCache（Elasticache for Redis/Memcached）

**ElastiCacheとは：**
- インメモリキャッシュサービス（RedisまたはMemcached）
- データベースの読み取り負荷を軽減し、パフォーマンスを向上させる
- よくアクセスされるデータをメモリにキャッシュして、データベースへのアクセスを減らす

**メリット：**
- 読み取りパフォーマンスを最大80倍高速化（AWSの主張）
- データベースの負荷を軽減し、コストを最大55%削減できる可能性
- 頻繁にアクセスされるデータ（例: チャンネル情報、動画一覧）を高速に取得可能

**このプロジェクトでの必要性：**
- **現時点では不要**（開発環境・小規模運用の場合）
  - このプロジェクトでは既にDynamoDBでキャッシュ制御を実装しています（`channel_update_cache`）
  - トラフィックが少ない開発環境では、ElastiCacheの追加コストがメリットを上回る可能性があります
- **将来的に必要になる可能性：**
  - トラフィックが増加し、データベースの読み取り負荷が高くなった場合
  - リアルタイムでのデータ取得が頻繁に必要になった場合
  - 複数のユーザーが同時にアクセスする本番環境の場合

**結論：** 開発環境では**スキップして問題ありません**。本番環境でトラフィックが増加した際に検討してください。

### RDS Proxy

**RDS Proxyとは：**
- データベース接続をプールして管理するプロキシサービス
- アプリケーションとデータベースの間に配置され、接続管理を簡素化
- 接続の再利用により、データベースへの接続数を削減

**メリット：**
- **接続プーリング**: 複数のLambda関数が同じデータベース接続を共有できる
- **スケーラビリティ**: Lambda関数が多数実行されても、データベースへの接続数を制御できる
- **耐障害性**: データベースの障害時に接続を自動的に切り替え
- **セキュリティ**: IAM認証をサポートし、パスワードを直接管理する必要がない

**このプロジェクトでの必要性：**
- **無料枠では利用不可**（重要）
  - RDS Proxyは無料プランアカウントでは利用できません
  - 「This feature isn't available with free plan accounts」というエラーが表示されます
  - 無料枠を使用している場合は、RDS Proxyをスキップして、Lambda関数から直接RDSに接続します
- **有料プランでは推奨（特にLambda関数を使用する場合）**
  - Lambda関数はサーバーレスで、同時実行数が変動する可能性がある
  - 各Lambda関数が個別にデータベースに接続すると、接続数が急増する可能性がある
  - RDS Proxyを使用することで、接続数を効率的に管理できる

**結論：** 
- **無料枠を使用している場合**: RDS Proxyは**スキップ**して、Lambda関数から直接RDSに接続します（セクション2を参照）
- **有料プランの場合**: RDS Proxyは設定することを推奨します。特にLambda関数からRDSに接続する場合は、接続管理が重要です

---

## 2. RDS Proxyの作成（無料枠ではスキップ）

**重要**: RDS Proxyは**無料プランアカウントでは利用できません**。無料枠を使用している場合は、このセクションをスキップして、Lambda関数から直接RDSに接続します（セクション4.3の環境変数設定で、`DB_HOST`にRDSのエンドポイントを設定します）。

有料プランを使用している場合のみ、以下の手順でRDS Proxyを作成してください。

### 2.1 RDS Proxyの作成

1. RDSコンソールで、左メニューから**プロキシ**を選択
2. **プロキシの作成**ボタンをクリック
3. 以下の設定を行う：

#### プロキシ設定

- **エンジンファミリー**: **MariaDB と MySQL**を選択
  - Aurora MySQL、RDS for MariaDB、RDS for MySQLをサポート
  - このプロジェクトではMySQLを使用しているため、このオプションを選択します

- **プロキシ識別子**: `youtube-dashboard-proxy`
  - プロキシの名前を入力します
  - AWSアカウント内で一意である必要があります
  - 1〜60文字以内で英数字またはハイフンのみ使用可能
  - 先頭は英文字、ハイフンの連続使用や末尾のハイフンは不可

- **アイドルクライアントの接続タイムアウト**: `00時間30分`（デフォルト）
  - アプリケーションからのアイドル接続が、指定した時間経過後に閉じられます
  - 最小1分、最大8時間
  - デフォルトの30分で問題ありません

#### ターゲットグループの設定

- **データベース**: `youtube-dashboard-db`（先ほど作成したRDSインスタンス）を選択
  - プロキシが接続するデータベースを指定します

- **ターゲット接続ネットワークタイプ**: **IPv4**を選択
  - リソースはIPv4アドレスプロトコルでのみ通信できます
  - ターゲットグループの各DBインスタンスにはIPv4アドレスが割り当てられている必要があります

- **接続プールの最大接続数**: `100%`（デフォルト）
  - データベースの最大接続制限に対する割合として、許可される最大接続数を指定します
  - 例: 最大接続数を5,000接続に設定した場合、100%を指定すると、プロキシはデータベースに対して最大5,000個の接続を作成できます
  - デフォルトの100%で問題ありませんが、必要に応じて調整可能です

- **リーダーエンドポイントを含める**: **チェックしない**
  - この機能は現在、単一の書き込みAuroraデータベースでのみ使用できます
  - RDS for MySQLでは使用できないため、チェックしないでください

#### 認証

**重要**: RDS Proxyは、データベースへの接続に認証情報が必要です。このプロジェクトでは環境変数から認証情報を取得していますが、RDS Proxy自体はSecrets Managerを使用する必要があります。

- **デフォルト認証スキーム**: **なし**（デフォルト）
  - プロキシへのクライアント接続とプロキシからデータベースへの接続にプロキシが使用するデフォルトの認証タイプを選択します
  - Secrets Managerを使用する場合は「なし」で問題ありません

- **IAMロール**: **IAMロールを作成**を選択
  - プロキシがAWS Secrets Managerシークレットにアクセスする際に使用するIAMロールを作成または選択します
  - 新規作成する場合は「IAMロールを作成」を選択します
  - **注意**: RDS ProxyはSecrets Managerを使用するため、IAMロールは必須です

- **Secrets Managerのシークレット**: **新しいシークレットを作成する**を選択
  - プロキシが使用できるデータベースユーザーアカウントの認証情報を表すSecrets Managerシークレットを作成または選択します
  - **このプロジェクトでは環境変数から認証情報を取得していますが、RDS Proxy自体はSecrets Managerを使用する必要があります**
  - 新規作成する場合：
    - シークレット名: `rds-proxy-credentials`（任意）
    - ユーザー名: RDSのマスターユーザー名（例: `admin`）
    - パスワード: RDSのマスターパスワード
    - **重要**: Lambda関数の環境変数`DB_USER`と`DB_PASSWORD`と同じ値を設定してください
  - 既存のシークレットを使用する場合は、該当するシークレットを選択します
  
  **補足説明**:
  - Lambda関数側では環境変数（`DB_USER`、`DB_PASSWORD`）から認証情報を取得してRDS Proxyに接続します
  - RDS Proxy側では、Secrets Managerから認証情報を取得してRDSデータベースに接続します
  - 両方で同じ認証情報を使用する必要がありますが、管理方法が異なります

- **クライアント認証タイプ**: **MySQL Caching Sha2 パスワード**を選択
  - プロキシへのクライアント接続に必要なパスワード認証のタイプを選択します
  - MySQL 8.0のデフォルト認証方式である`caching_sha2_password`を使用します
  - **注意**: プロキシへの接続時にTLSを使用しない場合、MySQL caching sha2パスワード認証には特定の制限があります。TLS接続を推奨します

- **IAM認証**: **許可されていません**（デフォルト）
  - プロキシへの接続には、データベース認証情報を指定する以外に、IAM認証を使用できます
  - 開発環境では「許可されていません」で問題ありません
  - 本番環境でセキュリティを強化する場合は、IAM認証を有効化することも可能です

#### 接続

- **Transport Layer Securityが必要**: **チェックする**（推奨）
  - Transport Layer Security (TLS)は、ネットワークを介した通信を保護する暗号化プロトコルです
  - セキュリティ上、TLS接続を有効にすることを強く推奨します
  - MySQL Caching Sha2パスワード認証を使用する場合、TLS接続が推奨されます

- **エンドポイントネットワークタイプ**: **IPv4**を選択
  - リソースはIPv4アドレス指定プロトコル経由でのみ通信できます
  - IPv6やデュアルスタックモードも選択可能ですが、通常はIPv4で問題ありません

- **サブネット**: **複数のサブネットを選択**（重要）
  - サブネットは、選択したVPCでデータベースが使用できるIP範囲を定義します
  - プロキシには、異なるアベイラビリティーゾーンで最低2つのサブネットが必要です
  - 可用性を向上させるため、複数のアベイラビリティーゾーンからサブネットを選択してください
  - 例: `subnet-098e7d2a17489fb65`, `subnet-0141f925c4b482f8d`, `subnet-06b2fcacbe2fa9582`

- **セキュリティグループ**: 新規作成または既存のものを選択
  - Lambda関数からRDS Proxyへのアクセスを許可するセキュリティグループを選択します
  - セクション7で作成したセキュリティグループを使用するか、新規作成します

#### 詳細設定

- **拡張されたログ記録**: **拡張ログ記録をアクティブ化**（オプション）
  - 拡張されたログ記録により、プロキシによって処理されたクエリの詳細がログに記録され、CloudWatch Logsに公開されます
  - デバッグやパフォーマンス分析に有用ですが、パフォーマンスを低下させる可能性があります
  - **注意**: 拡張ログ記録は24時間後に自動的に無効になります
  - 開発環境では有効化して問題ありませんが、本番環境では必要に応じて有効化してください

4. **プロキシの作成**ボタンをクリック
5. プロキシが作成されるまで待つ（数分かかります）
6. プロキシのエンドポイントをメモしておく（例: `youtube-dashboard-proxy.proxy-xxxxx.ap-northeast-1.rds.amazonaws.com`）
   - このエンドポイントをLambda関数の環境変数`DB_HOST`に設定します

---

## 3. DynamoDBテーブルの作成

### 3.0 DynamoDBをキャッシュに使う理由

このプロジェクトでは、DynamoDBを「データキャッシュ」ではなく「レート制限管理」のために使用しています。

#### DynamoDBの用途

**実際の使用目的：**
- YouTube APIのレート制限を回避するための更新頻度制御
- 各チャンネルの最終取得時刻（`last_fetched_at`）を保存
- `MIN_FETCH_INTERVAL`（デフォルト10分）以内のリクエストでは、YouTube APIを呼ばずにRDSから既存データを返す

**保存するデータ：**
- `youtube_channel_id`: チャンネルID（パーティションキー）
- `last_fetched_at`: 最終取得時刻（Unix time、ミリ秒）
- `etag`: YouTube APIのレスポンスETag（任意）

**動作の流れ：**
1. チャンネルインポートリクエストが来る
2. DynamoDBで`last_fetched_at`を確認
3. 10分以内なら → RDSから既存データを返す（YouTube APIを呼ばない）
4. 10分経過していれば → YouTube APIを呼び出し、RDSに保存、DynamoDBの`last_fetched_at`を更新

#### DynamoDB vs Redis（ElastiCache）の比較

| 項目 | DynamoDB | Redis（ElastiCache） |
|------|----------|---------------------|
| **用途** | レート制限管理（更新時刻の保存） | データキャッシュ（実際のデータを保存） |
| **速度** | 数ミリ秒〜数十ミリ秒 | 1ミリ秒以下（インメモリ） |
| **コスト** | 無料枠あり（25GB、読み込み/書き込み25ユニット） | 有料（最小インスタンスでも月額数千円） |
| **設定の複雑さ** | 低い（テーブル作成のみ） | 高い（VPC、セキュリティグループ、サブネット設定が必要） |
| **永続化** | 自動（デフォルトで有効） | オプション（RDB/AOF） |
| **スケーラビリティ** | 自動スケーリング | 手動スケーリング |
| **Lambdaとの統合** | 簡単（boto3で直接アクセス） | VPC設定が必要（コールドスタートが遅くなる） |

#### なぜDynamoDBを選んだのか

1. **無料枠がある**
   - DynamoDBは無料枠が充実（25GB、読み込み/書き込み25ユニット）
   - Redis（ElastiCache）は最小インスタンスでも月額数千円かかる

2. **設定が簡単**
   - DynamoDBはテーブル作成のみで使用可能
   - RedisはVPC、セキュリティグループ、サブネットの設定が必要
   - Lambda関数からVPC内のRedisにアクセスする場合、VPC設定が必要でコールドスタートが遅くなる

3. **サーバーレスに最適**
   - DynamoDBは完全マネージドで、サーバー管理不要
   - Lambda関数から直接アクセス可能（VPC設定不要）
   - 自動スケーリングでトラフィック増加に対応

4. **このプロジェクトの要件に適している**
   - 実際のデータはRDSに保存されている
   - DynamoDBは「いつ取得したか」というメタデータのみを保存
   - データ量が少ないため、速度差は実用上問題ない

#### Redisを使うべき場合

以下の場合はRedis（ElastiCache）を検討してください：

1. **実際のデータをキャッシュする場合**
   - チャンネル情報や動画一覧をキャッシュして、RDSへのアクセスを減らしたい
   - 頻繁にアクセスされるデータを高速に取得したい

2. **高トラフィック環境**
   - 1秒間に数千リクエストを処理する必要がある
   - ミリ秒単位の速度が重要

3. **複雑なキャッシュ戦略が必要**
   - TTL（Time To Live）の細かい制御
   - キャッシュの無効化（invalidation）
   - 複雑なデータ構造（リスト、セット、ハッシュなど）

#### このプロジェクトでの結論

**現時点ではDynamoDBで十分です**。理由：
- レート制限管理という単純な用途
- データ量が少ない（チャンネルIDとタイムスタンプのみ）
- 無料枠で運用可能
- 設定が簡単で、Lambda関数から直接アクセス可能

**将来的にRedisが必要になる場合：**
- トラフィックが増加し、実際のデータをキャッシュする必要が出てきた場合
- チャンネル情報や動画一覧を高速に取得する必要が出てきた場合

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

### 4.0 Lambda関数でPythonを選んだ理由

このプロジェクトでは、Lambda関数に**Python**を使用しています。フロントエンドはNext.js（TypeScript/JavaScript）ですが、バックエンドはPythonで実装されています。

#### Python vs Node.js（TypeScript/JavaScript）の比較

| 項目 | Python | Node.js（TypeScript/JavaScript） |
|------|--------|----------------------------------|
| **実行速度** | やや遅い（インタープリタ型） | 速い（V8エンジン、JITコンパイル） |
| **コールドスタート** | やや遅い（1-2秒） | 速い（数百ミリ秒） |
| **並列処理** | `ThreadPoolExecutor`で簡単 | `Promise.all`で簡単（非同期処理が得意） |
| **データ処理** | 優秀（pandas、numpyなど） | 標準ライブラリで対応可能 |
| **型安全性** | 型ヒント（Pydantic） | TypeScriptで強力 |
| **AWS SDK** | boto3（公式、充実） | AWS SDK v3（公式、充実） |
| **データベース** | pymysql、psycopg2 | mysql2、pg |
| **学習コスト** | 低い（シンプルな構文） | 中程度（非同期処理の理解が必要） |
| **エコシステム** | データ分析・機械学習に強い | Web開発に強い |

#### なぜPythonを選んだのか

1. **データ処理とAPI連携が得意**
   - YouTube APIからの大量データ（動画一覧、統計情報）を処理する必要がある
   - データの変換、正規化、バリデーションが簡単
   - `requests`ライブラリでHTTPリクエストが簡単

2. **並列処理が簡単**
   - `ThreadPoolExecutor`で複数のYouTube APIリクエストを並列実行
   - コードが読みやすく、理解しやすい
   ```python
   # Pythonの並列処理例（このプロジェクトで使用）
   with ThreadPoolExecutor(max_workers=10) as executor:
       futures = [executor.submit(fetch_chunk, chunk) for chunk in chunks]
       results = [future.result() for future in as_completed(futures)]
   ```

3. **型安全性とバリデーション**
   - Pydanticでリクエスト/レスポンスの型定義とバリデーションが簡単
   - 型ヒントでコードの可読性が向上

4. **AWS SDK（boto3）との統合**
   - DynamoDB、RDSへのアクセスが簡単
   - 公式SDKが充実している

5. **将来の拡張性**
   - Streamlitによる分析ダッシュボードもPythonで実装予定
   - データ分析ライブラリ（pandas、numpy）が豊富
   - 機械学習への拡張も容易

6. **コードの可読性**
   - シンプルで読みやすい構文
   - チーム開発で理解しやすい

#### Node.js（TypeScript）でも問題ない理由

実は、**Node.js（TypeScript）でも全く問題ありません**。以下の理由で選択可能です：

1. **実行速度が速い**
   - V8エンジンによる高速実行
   - コールドスタートが速い（数百ミリ秒）

2. **非同期処理が得意**
   - `Promise.all`で複数のAPIリクエストを並列実行
   - イベントループによる効率的な処理

3. **フロントエンドと同じ言語**
   - Next.jsと同じTypeScript/JavaScriptで統一できる
   - コードの共有が可能（型定義など）

4. **AWS SDK v3が充実**
   - モダンなAPI設計
   - TypeScriptの型定義が完備

#### Node.jsを使うべき場合

以下の場合はNode.jsを検討してください：

1. **フロントエンドとバックエンドを統一したい**
   - 同じ言語で開発したい
   - 型定義を共有したい

2. **実行速度が重要**
   - コールドスタートを最小化したい
   - 高トラフィック環境

3. **既存のNode.jsエコシステムを活用したい**
   - npmパッケージを活用したい
   - Express、Fastifyなどのフレームワークを使いたい

#### このプロジェクトでPythonを選んだ理由（まとめ）

**主な理由：**
- データ処理とAPI連携が得意
- 並列処理が簡単でコードが読みやすい
- Streamlitによる分析ダッシュボードもPythonで実装予定
- 将来のデータ分析・機械学習への拡張を考慮

**結論：**
- **Python**: データ処理、分析、将来の拡張性を重視する場合に適している
- **Node.js**: 実行速度、フロントエンドとの統一性を重視する場合に適している
- **どちらでも問題ない**: Lambda関数は両方の言語をサポートしており、プロジェクトの要件に応じて選択可能

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

**重要**: すべてのLambda関数は同じ依存関係（`common/`、`db/`、`services/`、`utils/`、`constants/`）を使用しているため、**同じZIPファイルをすべてのLambda関数で使用できます**。各Lambda関数では、ハンドラーのみを変更します。

1. ローカル環境でLambda関数用のZIPファイルを作成：

```bash
cd backend
zip -r lambda-functions.zip handlers/ services/ db/ common/ utils/ constants/ -x "*.pyc" "__pycache__/*"
```

**注意**: ZIPファイル名は任意です（例: `lambda-functions.zip`、`youtube-dashboard-backend.zip`など）。すべてのLambda関数で同じZIPファイルを使用します。

2. Lambdaコンソールで、作成した関数（`youtube-dashboard-channel-import`）を選択
3. **コード**タブを開く
4. **アップロード元**ドロップダウンから**ZIPファイルをアップロード**を選択
5. 作成したZIPファイルをアップロード
6. **ハンドラー**を`handlers.channel_import.lambda_handler`に設定
   - **ハンドラー**: Lambda関数が実行するエントリーポイント（Python関数）を指定します
   - 形式: `モジュールパス.関数名`
   - この関数では`handlers.channel_import.lambda_handler`を指定
   - **注意**: ハンドラーはAPIエンドポイントとは異なります（後述）

### 4.3 環境変数の設定

1. Lambda関数の**設定**タブを開く
2. **環境変数**セクションで**編集**をクリック
3. 以下の環境変数を追加：
   - `YOUTUBE_API_KEY`: YouTube Data API v3のAPIキー
   - `DB_HOST`: **RDSのエンドポイント**または**RDS Proxyのエンドポイント**
     - **無料枠を使用している場合**: RDSのエンドポイントを設定します
       - RDSコンソールで作成したデータベースを選択
       - **接続とセキュリティ**タブからエンドポイントをコピー（例: `youtube-dashboard-db.xxxxx.ap-northeast-1.rds.amazonaws.com`）
     - **有料プランでRDS Proxyを使用している場合**: RDS Proxyのエンドポイントを設定します
       - RDS Proxyコンソールで作成したプロキシのエンドポイントをコピー（例: `youtube-dashboard-proxy.proxy-xxxxx.ap-northeast-1.rds.amazonaws.com`）
   - `DB_USER`: RDSのマスターユーザー名（例: `admin`）
   - `DB_PASSWORD`: RDSのマスターパスワード
     - **注意**: このプロジェクトでは環境変数から直接取得します
     - RDS Proxyを使用している場合は、RDS ProxyのSecrets Managerに保存した値と同じパスワードを設定してください
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

同様の手順で、以下のLambda関数も作成してください。**すべて同じZIPファイル（`lambda-functions.zip`）を使用します**。各Lambda関数では、ハンドラーのみを変更します。

#### 4.6.1 `youtube-dashboard-list-channels`の作成

1. Lambdaコンソールで**関数の作成**ボタンをクリック
2. **一から作成**を選択
3. 以下の設定を行う：
   - **関数名**: `youtube-dashboard-list-channels`
   - **ランタイム**: Python 3.11 または 3.12
   - **アーキテクチャ**: x86_64
4. **関数の作成**ボタンをクリック
5. **コード**タブを開く
6. **アップロード元**ドロップダウンから**ZIPファイルをアップロード**を選択
7. **同じZIPファイル（`lambda-functions.zip`）をアップロード**
8. **ハンドラー**を`handlers.list_channels.lambda_handler`に設定
9. セクション4.3〜4.5の手順で、同じ環境変数、IAMロール、VPC設定を適用

#### 4.6.2 `youtube-dashboard-get-channel-detail`の作成

1. Lambdaコンソールで**関数の作成**ボタンをクリック
2. **一から作成**を選択
3. 以下の設定を行う：
   - **関数名**: `youtube-dashboard-get-channel-detail`
   - **ランタイム**: Python 3.11 または 3.12
   - **アーキテクチャ**: x86_64
4. **関数の作成**ボタンをクリック
5. **コード**タブを開く
6. **アップロード元**ドロップダウンから**ZIPファイルをアップロード**を選択
7. **同じZIPファイル（`lambda-functions.zip`）をアップロード**
8. **ハンドラー**を`handlers.get_channel_detail.lambda_handler`に設定
9. セクション4.3〜4.5の手順で、同じ環境変数、IAMロール、VPC設定を適用

#### 4.6.3 `youtube-dashboard-get-channel-videos`の作成

1. Lambdaコンソールで**関数の作成**ボタンをクリック
2. **一から作成**を選択
3. 以下の設定を行う：
   - **関数名**: `youtube-dashboard-get-channel-videos`
   - **ランタイム**: Python 3.11 または 3.12
   - **アーキテクチャ**: x86_64
4. **関数の作成**ボタンをクリック
5. **コード**タブを開く
6. **アップロード元**ドロップダウンから**ZIPファイルをアップロード**を選択
7. **同じZIPファイル（`lambda-functions.zip`）をアップロード**
8. **ハンドラー**を`handlers.get_channel_videos.lambda_handler`に設定
9. セクション4.3〜4.5の手順で、同じ環境変数、IAMロール、VPC設定を適用

**まとめ**:
- **ZIPファイル**: すべてのLambda関数で**同じZIPファイル（`lambda-functions.zip`）を使用**
- **ハンドラー**: 各Lambda関数で異なるハンドラーを指定
  - `youtube-dashboard-channel-import`: `handlers.channel_import.lambda_handler`
  - `youtube-dashboard-list-channels`: `handlers.list_channels.lambda_handler`
  - `youtube-dashboard-get-channel-detail`: `handlers.get_channel_detail.lambda_handler`
  - `youtube-dashboard-get-channel-videos`: `handlers.get_channel_videos.lambda_handler`
- **環境変数・IAMロール・VPC設定**: すべてのLambda関数で同じ設定を使用

---

## 5. API Gatewayの設定（フロントエンド担当者と協力）

### 5.0 HandlerとAPIエンドポイントの違い

**Handler（ハンドラー）**と**APIエンドポイント**は異なる概念です。混同しやすいので、明確に区別しましょう。

#### Handler（ハンドラー）とは

**Handler（ハンドラー）**は、プログラミング全般で使われる一般的な概念で、「イベントやリクエストを受け取って処理する関数」を指します。Pythonに限らず、多くのプログラミング言語やフレームワークで使われる用語です。

**一般的な意味**:
- **イベントハンドラー**: イベント（クリック、キー入力など）を受け取って処理する関数
- **リクエストハンドラー**: HTTPリクエストを受け取って処理する関数
- **エラーハンドラー**: エラーを受け取って処理する関数
- **シグナルハンドラー**: シグナルを受け取って処理する関数

**Lambda関数でのHandler**:
Lambda関数では、Handlerは**Lambda関数が実行される際に呼び出されるエントリーポイント（関数）**を指します。

- **役割**: Lambda関数が実行される際に呼び出されるエントリーポイント
- **場所**: Lambda関数のコード内（例: `handlers/channel_import.py`の`lambda_handler`関数）
- **形式**: `モジュールパス.関数名`（例: `handlers.channel_import.lambda_handler`）
- **設定場所**: Lambda関数の設定画面の「ハンドラー」フィールド
- **言語**: Pythonに限らず、Node.js、Java、Go、C#などでも同様の概念がある

**例（Python）**:
```python
# handlers/channel_import.py
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # この関数が「ハンドラー」
    # event: Lambda関数に渡されるイベントデータ
    # context: Lambda関数の実行コンテキスト
    logger.info("channel_import handler started")
    # ... 処理 ...
    return response
```

**例（Node.js/TypeScript）**:
```typescript
// handlers/channel_import.ts
export const handler = async (event: any, context: any) => {
    // この関数が「ハンドラー」
    // event: Lambda関数に渡されるイベントデータ
    // context: Lambda関数の実行コンテキスト
    console.log("channel_import handler started");
    // ... 処理 ...
    return response;
};
```

**他の文脈でのHandler例**:
- **Webフレームワーク（Express.js）**: リクエストハンドラー
  ```javascript
  app.get('/users', (req, res) => {
      // この関数が「リクエストハンドラー」
  });
  ```
- **イベント駆動（React）**: イベントハンドラー
  ```jsx
  <button onClick={() => handleClick()}>
      // handleClickが「イベントハンドラー」
  </button>
  ```
- **エラーハンドリング**: エラーハンドラー
  ```python
  try:
      # 処理
  except Exception as e:
      error_handler(e)  # エラーハンドラー
  ```

#### APIエンドポイントとは

**APIエンドポイント**は、API Gatewayで定義される**HTTP URLパス**のことです。

- **役割**: クライアント（フロントエンド）がアクセスするURL
- **場所**: API Gatewayの設定
- **形式**: `HTTPメソッド + パス`（例: `POST /channels/import`）
- **設定場所**: API Gatewayの設定画面

**例**:
- `POST /channels/import` → チャンネルをインポートするエンドポイント
- `GET /channels` → チャンネル一覧を取得するエンドポイント
- `GET /channels/{id}` → 特定のチャンネル詳細を取得するエンドポイント

#### 関係性

```
[フロントエンド]
  ↓ HTTPリクエスト
[API Gateway]
  POST /channels/import  ← APIエンドポイント
  ↓
[Lambda関数: youtube-dashboard-channel-import]
  ↓
[Handler: handlers.channel_import.lambda_handler]  ← ハンドラー（Python関数）
  ↓
[処理実行]
```

**具体例**:

| APIエンドポイント | Lambda関数名 | Handler |
|------------------|-------------|---------|
| `POST /channels/import` | `youtube-dashboard-channel-import` | `handlers.channel_import.lambda_handler` |
| `GET /channels` | `youtube-dashboard-list-channels` | `handlers.list_channels.lambda_handler` |
| `GET /channels/{id}` | `youtube-dashboard-get-channel-detail` | `handlers.get_channel_detail.lambda_handler` |
| `GET /channels/{id}/videos` | `youtube-dashboard-get-channel-videos` | `handlers.get_channel_videos.lambda_handler` |

#### まとめ

- **Handler**: Lambda関数内のPython関数（コード）
- **APIエンドポイント**: API Gatewayで定義されるHTTP URLパス（URL）
- **関係**: APIエンドポイント → Lambda関数 → Handler（関数）の順で実行される

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

## 6. Secrets Managerの設定について

### 6.1 RDS Proxy用のSecrets Manager設定（RDS Proxyを使用する場合のみ必須）

**重要**: 
- **無料枠を使用している場合**: RDS Proxyを使用しないため、Secrets Managerの設定は**不要**です。このセクションをスキップしてください。
- **有料プランでRDS Proxyを使用する場合**: Secrets Managerの設定は**必須**です。RDS Proxyはデータベースへの接続にSecrets Managerから認証情報を取得する必要があります。

RDS Proxyの作成時に、Secrets Managerのシークレットを作成する手順が含まれています（セクション2.1の「認証」セクションを参照）。

**RDS Proxy用のシークレット作成**（RDS Proxyを使用する場合のみ）:
- シークレット名: `rds-proxy-credentials`（RDS Proxy作成時に指定）
- ユーザー名: RDSのマスターユーザー名（例: `admin`）
- パスワード: RDSのマスターパスワード
- **重要**: Lambda関数の環境変数`DB_USER`と`DB_PASSWORD`と同じ値を設定してください

### 6.2 Lambda関数用のSecrets Manager設定（オプション）

**注意**: このプロジェクトでは、Lambda関数は環境変数から直接認証情報を取得しています（`constants/config.py`を参照）。そのため、Lambda関数用のSecrets Manager設定は**オプション**です。

もしLambda関数でもSecrets Managerを使用したい場合は、以下の手順で設定できます：

1. AWSコンソールで**Secrets Manager**サービスを開く
2. **新しいシークレットを保存**をクリック
3. **シークレットタイプ**: **その他のシークレット**を選択
4. **キー/値のペア**で以下のシークレットを作成：
   - `youtube-api-key`: YouTube Data API v3のAPIキー
   - `db-user`: RDSのマスターユーザー名
   - `db-password`: RDSのマスターパスワード
   - `db-host`: RDS Proxyのエンドポイント
   - `db-name`: データベース名
5. **シークレット名**: `youtube-dashboard-secrets`
6. **次へ**をクリックして保存

**Lambda関数でのSecrets Manager参照**:
- Lambda関数のコード内でSecrets Manager APIを使用して値を取得するように変更する必要があります
- 現在の実装（`constants/config.py`）では環境変数から取得しているため、コードの変更が必要です

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

1. **RDS作成時に「バックアップ保持期間が無料枠の制限を超えています」というエラーが発生する**
   - **原因**: 無料枠ではバックアップ保持期間が最大1日に制限されています
   - **解決方法**:
     1. RDS作成画面の「バックアップ」セクションを開く
     2. 「バックアップ保持期間」を**1日**に設定する
     3. デフォルトでは7日間などに設定されている場合があるため、必ず1日に変更してください
   - **注意**: 無料枠を使用する場合は、バックアップ保持期間を1日に設定する必要があります

2. **RDS Proxy作成時に「This feature isn't available with free plan accounts」というエラーが発生する**
   - **原因**: RDS Proxyは無料プランアカウントでは利用できません
   - **解決方法**:
     1. **RDS Proxyの作成をスキップ**してください（セクション2をスキップ）
     2. Lambda関数の環境変数`DB_HOST`に、**RDSのエンドポイント**を直接設定します
        - RDSコンソールで作成したデータベースを選択
        - **接続とセキュリティ**タブからエンドポイントをコピー（例: `youtube-dashboard-db.xxxxx.ap-northeast-1.rds.amazonaws.com`）
     3. Lambda関数から直接RDSに接続します（RDS Proxyは使用しません）
   - **注意**: 無料枠を使用している場合は、RDS Proxyは使用できません。Lambda関数から直接RDSに接続する設定で問題ありません

3. **Lambda関数がタイムアウトする**
   - タイムアウト設定を延長（最大15分）
   - メモリサイズを増やす

4. **RDSに接続できない**
   - セキュリティグループの設定を確認
   - VPC設定を確認
   - Lambda関数の環境変数`DB_HOST`が正しいエンドポイントを指しているか確認
     - 無料枠の場合: RDSのエンドポイントを設定
     - 有料プランでRDS Proxyを使用している場合: RDS Proxyのエンドポイントを設定
   - RDS Proxyを使用している場合は、RDS Proxyの設定も確認

5. **DynamoDBにアクセスできない**
   - IAMロールにDynamoDBの権限があるか確認
   - テーブル名が正しいか確認

6. **YouTube APIのエラー**
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


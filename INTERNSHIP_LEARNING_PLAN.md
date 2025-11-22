# インターンシップ選考に向けた学習プラン

## 概要

このドキュメントは、インターンシップ選考に向けて、現在のYouTubeダッシュボードプロジェクトを基に、さらなる学習を進めるためのプランです。

## インターンシップ要件との比較

### インターンシップで使用するテンプレート構成

- **フロントエンド**: Reactで、S3にデプロイ
- **バックエンド**: API Gateway + Lambda + RDS Proxy + RDSでREST APIを構成
- **参考**: Streamlitを利用したWebアプリ構築例

### 現在の実装状況

#### ✅ 実装済み

1. **フロントエンド（Next.js/React）**
   - チャンネル登録フォーム
   - チャンネル一覧・詳細ページ
   - 動画一覧ページ（ソート・フィルター機能付き）
   - 簡易グラフ（TopVideosChart、MonthlyViewsChart）
   - 型安全なAPI連携

2. **バックエンド（AWS Lambda + RDS）**
   - POST /channels/import
   - GET /channels
   - GET /channels/{id}
   - GET /channels/{id}/videos
   - RDS Proxy経由でのデータベース接続
   - DynamoDBによるキャッシュ制御
   - YouTube Data API連携

3. **インフラ設定**
   - API Gateway（HTTP API）の設定
   - CORS設定
   - Lambda関数のデプロイ
   - RDS（MySQL）データベース

#### ❌ 未実装・学習が必要な項目

1. **Streamlit分析ダッシュボード**
   - チャンネル選択機能
   - 指標選択（再生数、いいね数、コメント数）
   - 曜日 × 時間帯ヒートマップ
   - 動画長さ vs 再生数の散布図
   - 公開から30日間の成長カーブ比較
   - タグ別の平均パフォーマンス

2. **S3 + CloudFrontへのデプロイ**
   - Next.jsアプリの静的エクスポート
   - S3バケットへのデプロイ
   - CloudFrontディストリビューションの設定
   - 現在はNext.jsなのでVercelにデプロイしている可能性が高い

3. **AWS CLIを使った自動化**
   - デプロイスクリプトの作成
   - インフラのコード化（Terraform/CDK）

---

## 段階的な学習プラン

### Phase 1: Streamlitダッシュボードの実装（優先度：高）

**目標**: インターンシップの参考例として挙げられているStreamlitを実装し、データ分析の経験を積む

**重要**: StreamlitはLambda関数として実行できません。詳細は`STREAMLIT_ARCHITECTURE.md`を参照してください。

**理由**:
- StreamlitはWebSocketを使用するため、Lambdaの制約と適合しない
- Streamlitはステートフルなアプリケーションで、セッション状態を保持する必要がある
- Lambdaはリクエスト/レスポンス型の短時間処理に最適化されている

**推奨実行環境**:
- **開発環境**: EC2インスタンスまたはローカル環境
- **本番環境**: ECS Fargate（将来的に）

#### 1.1 環境構築

```bash
# backend/streamlit/requirements.txtを作成（Lambdaとは別の依存関係）
streamlit>=1.28.0
plotly>=5.17.0  # インタラクティブなグラフ用
pandas>=2.0.0   # データ分析用
pymysql>=1.1.0  # RDS接続用（既存のものを再利用）
```

#### 1.2 ディレクトリ構造

```
backend/
├── streamlit/
│   ├── app.py              # メインのStreamlitアプリ
│   ├── Dockerfile          # Dockerイメージの定義（ECS Fargate用）
│   ├── requirements.txt    # Streamlit用の依存関係（Lambdaとは別）
│   ├── pages/              # 複数ページがある場合
│   │   └── analysis.py
│   └── utils/
│       ├── db_connection.py # RDS接続ユーティリティ（既存のdb/rds.pyを再利用）
│       └── data_processor.py # データ処理関数
```

**注意**: StreamlitはLambdaとは別の実行環境で動作するため、依存関係も分離します。

#### 1.3 実装すべき機能

1. **チャンネル選択機能**
   - RDSからチャンネル一覧を取得
   - セレクトボックスまたは検索機能で選択
   - channelId直接入力も可能にする

2. **指標選択機能**
   - 再生数（view_count）
   - いいね数（like_count）
   - コメント数（comment_count）
   - ラジオボタンまたはセレクトボックスで選択

3. **曜日 × 時間帯ヒートマップ**
   - `published_at`から曜日と時間帯を抽出
   - 選択した指標の平均値を計算
   - Plotlyのヒートマップで可視化

4. **動画長さ vs 再生数の散布図**
   - X軸: `duration_sec`
   - Y軸: 選択した指標
   - Plotlyの散布図で可視化
   - ホバーで動画タイトルを表示

5. **公開から30日間の成長カーブ比較**
   - `video_stats_history`テーブルから時系列データを取得
   - 複数動画の成長カーブをオーバーレイ表示
   - 動画を選択できるUI

6. **タグ別の平均パフォーマンス**
   - `videos.tags_json`からタグを抽出
   - タグごとに平均パフォーマンスを計算
   - バーグラフまたはテーブルで表示

#### 1.4 学習リソース

- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [Streamlitを利用したWebアプリ構築例](https://qiita.com/tamura__246/items/366b5581c03dd74f4508)
- [Plotly公式ドキュメント](https://plotly.com/python/)

#### 1.5 実装のポイント

- RDSへの接続は`backend/db/rds.py`の`get_db_connection()`を再利用
- データ処理は関数として分離し、再利用可能にする
- Streamlitのキャッシュ機能（`@st.cache_data`）を活用してパフォーマンスを最適化
- エラーハンドリングを適切に実装
- **実行環境**: ローカル環境またはEC2で実行（Lambdaではない）
- **デプロイ**: 開発環境ではEC2、本番環境ではECS Fargateを検討

#### 1.6 実行方法

**ローカル環境での実行**:
```bash
cd backend/streamlit
pip install -r requirements.txt
streamlit run app.py
```

**Dockerでの実行**:
```bash
cd backend
docker build -t streamlit-app -f streamlit/Dockerfile .
docker run -p 8501:8501 streamlit-app
```

**EC2での実行（AWSマネジメントコンソールGUI手順）**:
1. **EC2インスタンスの作成**
   - コンソール上で`EC2 > インスタンス > インスタンスを起動`を選択
   - 推奨: Amazon Linux 2023 (x86) or Ubuntu 22.04 LTS、t3.small以上
   - キーペアは新規作成 or 既存を選択しダウンロード
   - ネットワークは`デフォルトVPC`でOK。セキュリティグループは後で編集するので一旦SSH(22)のみ許可でも可
   - 「高度な詳細」>「ユーザーデータ」にDockerインストールスクリプトを貼り付けると後作業が楽（例: Amazon Linuxなら`yum update -y && yum install docker -y && service docker start`）
2. **Dockerインストール（GUIのみで完結したい場合）**
   - `Systems Manager > セッションマネージャ`を使ってシェルに入り、`sudo yum install docker -y`（AL2023）を実行
   - もしくはCloudShellから`aws ssm start-session --target <instance-id>`で入って同様のコマンドを実行
   - 実行後`sudo usermod -aG docker ec2-user`、`sudo systemctl enable docker && sudo systemctl start docker`
3. **Dockerイメージの取得と実行**
   - `ECR`を使う場合: `ECR > リポジトリ`でイメージをpushしておき、コンソールの`接続`ボタンから`docker pull <account>.dkr.ecr....`スクリプトをコピー
   - ローカルDockerイメージを使う場合は`docker save`→`S3アップロード`→EC2で`aws s3 cp`→`docker load`などGUI操作とCLIを組み合わせる
   - 起動コマンド例：`docker run -d -p 8501:8501 --env-file .env streamlit-app:latest`
4. **セキュリティグループでポート8501を開放**
   - コンソールの`EC2 > セキュリティグループ`で対象SGを選択し`インバウンドルールを編集`
   - ルール追加: タイプ=`カスタムTCP`, ポート範囲=`8501`, 送信元=`自分のグローバルIP`（`0.0.0.0/0`は開発中のみ）
   - 保存後、`http://<PublicIPv4>:8501`にブラウザでアクセスしてStreamlitが表示されることを確認

#### 1.7 追加で実装したい分析アイデア

| 分析テーマ | 内容 | 実装メモ | 期待できる学び |
| --- | --- | --- | --- |
| コホート分析 | 動画の公開月をコホートに分け、公開後30日/90日の累計指標を比較 | `video_stats_history`を公開月でグループ化し、Plotlyの`px.line`や`px.area`で描画 | 時系列データ整形やウィンドウ関数の理解 |
| 成長率・異常検知 | 日次指標のデルタや移動平均から急伸/急落をハイライト | pandasの`pct_change()`や`rolling()`で変化率を算出し、Plotlyで条件付きカラーリング | アラートロジック設計、データクレンジング |
| タグ組み合わせ分析 | よく一緒に使われるタグのセットを抽出し、パフォーマンスを算出 | `itertools.combinations`でタグペアを生成、`groupby`で平均指標を計算 | マルチキー集計や相関解釈 |
| ファネル/リテンション指標 | 視聴 → いいね → コメントのコンバージョン率を可視化 | 指標の比率を算出し`plotly.graph_objects.Funnel`で描画 | ビジネスメトリクスの設計 |
| 収益シミュレーション | 推定RPM/CPMを仮定し、動画ごとの想定収益を算出 | RPMをサイドバーで入力させ、`view_count * rpm / 1000`で算出 | 仮説検証とWhat-if分析 |
| 比較ダッシュボード | 複数チャンネルを並列比較し、指標差分やランキングを表示 | `st.multiselect`で複数チャンネルを選択し、Plotlyの`px.bar`/`px.scatter`で比較 | 構造化データの標準化、UI/UX設計 |
| 自動インサイト生成 | 指標の上位/下位をテキストで要約 | pandasでランキング後に`st.markdown`で文章化。将来的にLLM連携も検討 | データ説明力、レポーティング |
| 配信スケジュール最適化 | 曜日×時間帯ヒートマップから「次の公開候補」を提示 | ヒートマップデータの上位セルを抽出し提案文を生成 | 既存分析結果のアクション化 |

##### 実装順の目安
1. **異常検知/成長率**: 既存データを加工するだけで実装できる
2. **タグ組み合わせ分析**: pandas整形スキルを強化
3. **コホート分析・比較ダッシュボード**: データ量が増えるほど価値が高まる
4. **収益シミュレーション / 自動インサイト**: ビジネス文脈でのアウトプットを磨ける

##### 実装時のヒント
- Streamlitの`st.expander`で分析ごとに折りたたみUIを用意すると閲覧しやすい
- 計算コストが高い処理は`@st.cache_data(show_spinner=False)`でキャッシュ
- ロジックは`backend/streamlit/utils/`配下に切り出し、単体テストを追加
- 初期検証はCSVなどのモックデータでグラフを作り、動作確認後にRDS接続へ差し替える

### Phase 2: S3 + CloudFrontへのデプロイ（優先度：中）

**目標**: インターンシップのテンプレート構成に合わせて、ReactアプリをS3にデプロイする経験を積む

#### 2.1 Next.jsの静的エクスポート

Next.jsアプリを静的サイトとしてエクスポートする必要があります。

**注意**: Next.jsのApp Routerを使用している場合、一部の機能（Server Components、API Routes）は静的エクスポートでは使用できません。

**対応方法**:
1. すべてのページをClient Componentsにする（`'use client'`を追加）
2. API呼び出しはクライアント側で行う（既に実装済み）
3. `next.config.ts`で静的エクスポートを有効化

```typescript
// next.config.ts
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true, // S3では画像最適化が使えないため
  },
}
```

#### 2.2 S3バケットの作成と設定

1. S3バケットを作成
2. 静的ウェブホスティングを有効化
3. バケットポリシーを設定（CloudFrontからのアクセスを許可）

#### 2.3 CloudFrontディストリビューションの作成

1. オリジンとしてS3バケットを設定
2. デフォルトルートオブジェクトを`index.html`に設定
3. エラーページの設定（404エラー時も`index.html`を返す）
4. HTTPSを有効化（ACMで証明書を取得）

#### 2.4 デプロイスクリプトの作成

```bash
# scripts/deploy-frontend.sh
#!/bin/bash
npm run build
aws s3 sync out/ s3://your-bucket-name --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

#### 2.5 学習リソース

- [CloudFront×S3でのホスティング（AWS公式）](https://aws.amazon.com/jp/premiumsupport/knowledge-center/cloudfront-serve-static-website/)
- [Next.js Static Exports](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)

### Phase 3: AWS CLIを使った自動化（優先度：低）

**目標**: インフラのコード化とデプロイの自動化を経験する

#### 3.1 デプロイスクリプトの拡張

- Lambda関数のデプロイ自動化
- 環境変数の設定自動化
- API Gatewayの設定確認

#### 3.2 Infrastructure as Code（IaC）

- TerraformまたはAWS CDKを使用
- インフラのコード化を学習
- バージョン管理と再現性の確保

#### 3.3 学習リソース

- [AWS CLI公式ドキュメント](https://aws.amazon.com/jp/cli/)
- [Terraform公式ドキュメント](https://www.terraform.io/docs)
- [AWS CDK公式ドキュメント](https://aws.amazon.com/jp/cdk/)

---

## 実装の優先順位

### 最優先（インターンシップ前に完了）

1. **Streamlitダッシュボードの実装**
   - インターンシップの参考例として挙げられている
   - データ分析の経験を積める
   - 実装期間: 1-2週間

### 次に優先（時間があれば）

2. **S3 + CloudFrontへのデプロイ**
   - インターンシップのテンプレート構成に合わせる
   - ただし、Next.jsの静的エクスポートには制限がある
   - 実装期間: 1週間

### 余裕があれば

3. **AWS CLIを使った自動化**
   - インフラのコード化を学習
   - 実装期間: 1-2週間

---

## 学習の進め方

### 1. Streamlitダッシュボードの実装から始める

**理由**:
- インターンシップの参考例として挙げられている
- データ分析の経験を積める
- 既存のRDSデータベースを活用できる
- 比較的短期間で実装可能

**ステップ**:
1. `backend/streamlit/app.py`を作成
2. RDS接続機能を実装
3. チャンネル選択機能を実装
4. 各分析機能を段階的に実装
5. UI/UXを改善

### 2. 実装しながら学ぶ

- 公式ドキュメントを参照しながら実装
- エラーが発生したら、エラーメッセージを読んで解決
- コードレビューを自分で行い、リファクタリングを実施

### 3. ドキュメント化

- 実装した機能の説明をREADMEに追加
- 使い方を記載
- トラブルシューティング情報を追加

---

## 参考リンク

### インターンシップで提供された参考ページ

- [API GatewayからのLambda呼び出し](https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/services-apigateway.html)
- [LambdaからのRDS呼び出し](https://aws.amazon.com/jp/blogs/news/using-amazon-rds-proxy-with-aws-lambda/)
- [CloudFront×S3でのホスティング](https://aws.amazon.com/jp/premiumsupport/knowledge-center/cloudfront-serve-static-website/)
- [Reactでの非同期処理](https://www.freecodecamp.org/japanese/news/how-to-use-axios-with-react/)
- [テンプレートと近い構成の実装例](https://dev.classmethod.jp/articles/react-api-gateway-lambda-dynamodb-viewcount/)
- [Streamlitを利用したWebアプリ構築例](https://qiita.com/tamura__246/items/366b5581c03dd74f4508)

### Streamlit関連の参考リンク

- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [StreamlitのアーキテクチャとAWSでの実行方法](./STREAMLIT_ARCHITECTURE.md)（このプロジェクト内のドキュメント）
- [AWSで構築するStreamlitアプリケーション基盤](https://zenn.dev/dataheroes/articles/20250608-streamlit-in-aws)
- [Plotly公式ドキュメント](https://plotly.com/python/)

### 追加の学習リソース

- [Next.js公式ドキュメント](https://nextjs.org/docs)
- [AWS公式ドキュメント](https://docs.aws.amazon.com/)

---

## チェックリスト

### Streamlitダッシュボード

- [ ] 環境構築（requirements.txtに追加）
- [ ] ディレクトリ構造の作成
- [ ] RDS接続機能の実装
- [ ] チャンネル選択機能
- [ ] 指標選択機能
- [ ] 曜日 × 時間帯ヒートマップ
- [ ] 動画長さ vs 再生数の散布図
- [ ] 公開から30日間の成長カーブ比較
- [ ] タグ別の平均パフォーマンス
- [ ] UI/UXの改善
- [ ] エラーハンドリングの実装
- [ ] READMEの更新

### S3 + CloudFrontデプロイ

- [ ] Next.jsの静的エクスポート設定
- [ ] S3バケットの作成
- [ ] CloudFrontディストリビューションの作成
- [ ] デプロイスクリプトの作成
- [ ] 動作確認

### AWS CLI自動化

- [ ] Lambda関数のデプロイ自動化
- [ ] 環境変数の設定自動化
- [ ] API Gatewayの設定確認スクリプト
- [ ] Infrastructure as Code（IaC）の学習

---

## まとめ

インターンシップ選考に向けて、以下の順序で学習を進めることを推奨します：

1. **Streamlitダッシュボードの実装**（最優先）
   - インターンシップの参考例として挙げられている
   - データ分析の経験を積める
   - 既存のRDSデータベースを活用できる

2. **S3 + CloudFrontへのデプロイ**（時間があれば）
   - インターンシップのテンプレート構成に合わせる
   - ただし、Next.jsの静的エクスポートには制限がある

3. **AWS CLIを使った自動化**（余裕があれば）
   - インフラのコード化を学習

現在のプロジェクトは、インターンシップのテンプレート構成と非常に近い状態にあります。Streamlitダッシュボードを実装することで、データ分析の経験を積み、インターンシップ選考に備えることができます。


# Streamlitの仕様とAWSでの実行方法

## Streamlitとは

Streamlitは、Pythonでデータサイエンスや機械学習の結果を手軽にWebアプリケーションとして可視化するためのフレームワークです。

### 基本的な仕様

1. **Pythonフレームワーク**
   - Pythonで書かれたコードをWebアプリケーションに変換
   - `streamlit run app.py`でローカルサーバーを起動

2. **サーバーサイドで実行**
   - Streamlitアプリは常にサーバー上で実行される
   - ブラウザはクライアントとして接続

3. **WebSocketを使用**
   - リアルタイムでUIを更新するためにWebSocketを使用
   - ユーザーの操作（ボタンクリック、入力変更など）をサーバーに送信
   - サーバーからの更新をリアルタイムで受信

4. **ステートフルなアプリケーション**
   - セッション状態を保持
   - ユーザーごとに独立したセッションを管理

## AWS Lambdaでは実行できない理由

### Lambdaの制約

1. **リクエスト/レスポンス型**
   - Lambdaは短時間のリクエスト/レスポンス型の処理に最適化
   - 最大実行時間: 15分（通常は数秒〜数分）
   - 長時間実行されるアプリケーションには不向き

2. **WebSocketの制約**
   - LambdaはWebSocketを直接サポートしていない
   - API Gateway WebSocket APIを使用する必要があるが、Streamlitのアーキテクチャとは適合しない

3. **ステート管理の制約**
   - Lambdaはステートレス（状態を保持しない）
   - Streamlitはセッション状態を保持する必要がある

4. **パッケージサイズの制限**
   - Lambdaのデプロイパッケージサイズに制限がある
   - Streamlitとその依存関係は比較的大きい

### 結論

**StreamlitはLambda関数として直接実行することはできません。**

## AWS上でのStreamlitの実行方法

### 1. Amazon ECS + Fargate（推奨）

**特徴**:
- サーバーレスなコンテナ実行環境
- 自動スケーリング
- 従量課金（使用した分だけ課金）

**構成**:
```
[ユーザー] → [Application Load Balancer] → [ECS Fargate] → [Streamlit App]
                                                              ↓
                                                          [RDS]
```

**メリット**:
- サーバー管理が不要
- 自動スケーリング
- コスト効率が良い（使用した分だけ課金）

**デメリット**:
- 設定がやや複雑
- コンテナイメージのビルドとデプロイが必要

### 2. Amazon EC2

**特徴**:
- 従来の仮想サーバー
- 完全な制御が可能
- 常時起動が必要

**構成**:
```
[ユーザー] → [EC2インスタンス] → [Streamlit App]
                                  ↓
                              [RDS]
```

**メリット**:
- シンプルで理解しやすい
- 完全な制御が可能
- 開発・テスト環境に適している

**デメリット**:
- サーバー管理が必要
- 常時起動のためコストがかかる
- スケーリングは手動

### 3. AWS App Runner

**特徴**:
- マネージドなコンテナ実行サービス
- 自動スケーリング
- シンプルな設定

**構成**:
```
[ユーザー] → [App Runner] → [Streamlit App]
                              ↓
                          [RDS]
```

**メリット**:
- 設定が簡単
- 自動スケーリング
- サーバー管理が不要

**デメリット**:
- 比較的新しいサービス（2021年リリース）
- カスタマイズの自由度がやや低い

### 4. Amazon Lightsail

**特徴**:
- シンプルで低コスト
- 固定料金
- 開発・小規模運用に適している

**構成**:
```
[ユーザー] → [Lightsail Container] → [Streamlit App]
                                      ↓
                                  [RDS]
```

**メリット**:
- シンプルで理解しやすい
- 低コスト（固定料金）
- 開発環境に適している

**デメリット**:
- スケーリングの自由度が低い
- 大規模運用には不向き

## このプロジェクトでの推奨実装方法

### 推奨: ECS Fargate（本番環境）またはEC2（開発環境）

**理由**:
1. **既存のRDSとの統合**
   - StreamlitはRDSに直接接続する必要がある
   - VPC内からのアクセスが必要
   - ECS FargateやEC2はVPC内で実行できる

2. **コスト効率**
   - 開発環境: EC2（t3.microなど、無料枠あり）
   - 本番環境: ECS Fargate（使用した分だけ課金）

3. **スケーラビリティ**
   - ECS Fargateは自動スケーリングに対応
   - トラフィックに応じてコンテナ数を調整

### 実装の流れ

#### 1. Dockerイメージの作成

```dockerfile
# backend/streamlit/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Streamlitアプリをコピー
COPY streamlit/ ./streamlit/

# ポートを公開
EXPOSE 8501

# Streamlitを起動
CMD ["streamlit", "run", "streamlit/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2. ローカルでの実行

```bash
# ローカルでテスト
cd backend
docker build -t streamlit-app -f streamlit/Dockerfile .
docker run -p 8501:8501 streamlit-app
```

#### 3. ECS Fargateへのデプロイ

1. ECR（Elastic Container Registry）にイメージをプッシュ
2. ECSクラスターとタスク定義を作成
3. Fargateでタスクを実行
4. Application Load Balancerを設定（オプション）

#### 4. EC2での実行（開発環境）

1. EC2インスタンスを作成
2. Dockerをインストール
3. イメージをプルして実行
4. セキュリティグループでポート8501を開放

## Streamlitのモジュール構成

### 主要なモジュール

1. **streamlit**（コアモジュール）
   - `st.write()`: データを表示
   - `st.title()`, `st.header()`: タイトル・見出し
   - `st.selectbox()`, `st.slider()`: UIコンポーネント
   - `st.plotly_chart()`: グラフ表示

2. **streamlit.cache**（キャッシュ機能）
   - `@st.cache_data`: データのキャッシュ
   - `@st.cache_resource`: リソースのキャッシュ

3. **streamlit.session_state**（セッション状態）
   - ユーザーごとの状態を保持

### 使用例

```python
import streamlit as st
import plotly.express as px
from db.rds import get_db_connection

# ページ設定
st.set_page_config(page_title="YouTube分析ダッシュボード", layout="wide")

# チャンネル選択
with get_db_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, title FROM channels")
        channels = cursor.fetchall()

channel_id = st.selectbox("チャンネルを選択", options=[c["id"] for c in channels])

# データ取得（キャッシュを使用）
@st.cache_data
def get_video_data(channel_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM videos WHERE channel_id = %s", (channel_id,))
            return cursor.fetchall()

videos = get_video_data(channel_id)

# グラフ表示
fig = px.scatter(videos, x="duration_sec", y="view_count")
st.plotly_chart(fig)
```

## まとめ

### Streamlitの特徴

- **Lambdaでは実行できない**: WebSocketとステート管理が必要なため
- **サーバーサイドで実行**: 常にサーバー上で実行される
- **WebSocketを使用**: リアルタイム更新のため

### AWS上での実行方法

1. **ECS Fargate**（本番環境・推奨）
   - サーバーレス、自動スケーリング
   - コスト効率が良い

2. **EC2**（開発環境・推奨）
   - シンプル、理解しやすい
   - 開発・テストに適している

3. **App Runner**（オプション）
   - マネージド、設定が簡単

4. **Lightsail**（オプション）
   - 低コスト、小規模運用

### このプロジェクトでの実装

- **開発環境**: EC2で実行（ローカル開発も可能）
- **本番環境**: ECS Fargateで実行（将来的に）
- **データ取得**: RDSに直接接続（既存の`db/rds.py`を再利用）


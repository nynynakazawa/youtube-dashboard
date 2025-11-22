# Streamlitダッシュボード クイックスタートガイド

## ローカル環境での実行

### 1. 依存関係のインストール

```bash
cd backend/streamlit
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成するか、環境変数を設定：

```bash
# .envファイルを作成
cat > .env << EOF
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-password
DB_NAME=analytics
EOF
```

または、環境変数を直接設定：

```bash
export DB_HOST=your-rds-endpoint.rds.amazonaws.com
export DB_USER=admin
export DB_PASSWORD=your-password
export DB_NAME=analytics
```

### 3. アプリケーションの起動

```bash
# backendディレクトリから実行
cd backend
streamlit run streamlit/app.py
```

ブラウザで `http://localhost:8501` にアクセスします。

## EC2での実行

### 1. EC2インスタンスの準備

**重要**: EC2インスタンスとECR（Elastic Container Registry）は**別物**です。

- **EC2**: 仮想サーバー（コンピューティングリソース）。アプリケーションを実行する場所
- **ECR**: Dockerコンテナイメージのレジストリ（ストレージサービス）。Dockerイメージを保存する場所

#### 1.1 キーペアの作成

**キーペアとは？**
- EC2インスタンスにSSH接続する際に使用する認証情報
- 公開鍵と秘密鍵のペア
- 秘密鍵（`.pem`ファイル）は**一度だけダウンロード可能**なので、必ず安全に保管してください

**AWSマネジメントコンソールでの作成方法**:

1. **AWSコンソールにログイン**
   - https://console.aws.amazon.com/ にアクセス
   - リージョンを選択（例: `ap-northeast-1`（東京））

2. **EC2サービスを開く**
   - サービス検索で「EC2」と入力して選択
   - 左側のメニューから「キーペア」を選択

3. **キーペアを作成**
   - 「キーペアを作成」ボタンをクリック
   - **キーペア名**: 任意の名前を入力（例: `youtube-dashboard-key`）
   - **キーペアタイプ**: `RSA`を選択（デフォルト）
   - **プライベートキーファイル形式**: `.pem`を選択（macOS/Linux用）または`.ppk`（Windows用）
   - 「キーペアを作成」ボタンをクリック

4. **秘密鍵をダウンロード**
   - 自動的にダウンロードが開始されます
   - ダウンロードした`.pem`ファイルを安全な場所に保存
   - **重要**: このファイルは**一度だけダウンロード可能**です。紛失した場合は新しいキーペアを作成する必要があります

5. **秘密鍵の権限を設定（macOS/Linux）**
   ```bash
   # ダウンロードしたキーファイルの権限を変更
   chmod 400 ~/Downloads/youtube-dashboard-key.pem
   # または、より安全な場所に移動
   mv ~/Downloads/youtube-dashboard-key.pem ~/.ssh/
   chmod 400 ~/.ssh/youtube-dashboard-key.pem
   ```

**AWS CLIでの作成方法**:

```bash
# キーペアを作成（秘密鍵を自動的に保存）
aws ec2 create-key-pair \
  --key-name youtube-dashboard-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/youtube-dashboard-key.pem

# 権限を設定
chmod 400 ~/.ssh/youtube-dashboard-key.pem

# 確認
aws ec2 describe-key-pairs --key-names youtube-dashboard-key
```

**既存のキーペアを使用する場合**:
- インスタンス作成時に「既存のキーペアを選択」から選択できます
- 新しいキーペアを作成する必要はありません

#### 1.2 EC2インスタンスの作成方法

**AWSマネジメントコンソールでの作成**:

1. **EC2コンソールを開く**
   - サービス検索で「EC2」と入力して選択
   - 「インスタンスを起動」ボタンをクリック

2. **名前とタグ**
   - インスタンス名を入力（例: `youtube-dashboard-streamlit`）

3. **アプリケーションとOSイメージ（AMI）**
   - **Amazon Linux 2023** または **Ubuntu 22.04 LTS** を選択
   - 無料利用枠の場合は「無料利用枠の対象」と表示されているものを選択

4. **インスタンスタイプ**
   - **t3.small**以上を推奨（Streamlitアプリの実行に十分なリソース）
   - 無料利用枠の場合は`t2.micro`または`t3.micro`を選択（制限あり）

5. **キーペア（ログイン情報）**
   - 「既存のキーペアを選択」から、先ほど作成したキーペアを選択
   - または「新しいキーペアを作成」から新規作成

6. **ネットワーク設定**
   - **VPC**: デフォルトVPCでOK
   - **セキュリティグループ**: 新しいセキュリティグループを作成
     - **SSH（ポート22）**: 自分のIPアドレスからのみ許可（推奨）
     - **カスタムTCP（ポート8501）**: 0.0.0.0/0（すべてのIP）から許可（Streamlitアプリ用）
   - **注意**: 本番環境では、ポート8501へのアクセスを特定のIPアドレスのみに制限することを推奨

7. **ストレージ**
   - デフォルト設定（8GB）でOK
   - 必要に応じて増やすことができます

8. **高度な詳細（オプション）**
   - ユーザーデータにDockerインストールスクリプトを貼り付けると便利：
   ```bash
   #!/bin/bash
   yum update -y
   yum install docker -y
   service docker start
   usermod -aG docker ec2-user
   ```

9. **インスタンスを起動**
   - 「インスタンスを起動」ボタンをクリック
   - インスタンスの状態が「実行中」になるまで待機（1-2分）

10. **パブリックIPアドレスを確認**
    - インスタンス一覧から、作成したインスタンスを選択
    - 「パブリックIPv4アドレス」をメモ（SSH接続に使用）

**SSH接続の確認**:

```bash
# Amazon Linux 2023の場合
ssh -i ~/.ssh/youtube-dashboard-key.pem ec2-user@<パブリックIPアドレス>

# Ubuntu 22.04の場合
ssh -i ~/.ssh/youtube-dashboard-key.pem ubuntu@<パブリックIPアドレス>

# 初回接続時は「Are you sure you want to continue connecting?」と聞かれるので「yes」と入力
```

**接続できない場合のトラブルシューティング**:
- セキュリティグループでSSH（ポート22）が自分のIPアドレスから許可されているか確認
- キーファイルの権限が正しいか確認（`chmod 400`）
- インスタンスの状態が「実行中」になっているか確認
- パブリックIPアドレスが正しいか確認

**ECRは必要？**:
- EC2で直接Pythonを実行する場合: **ECRは不要**
- EC2でDockerコンテナを実行する場合: **ECRを使用可能**（オプション）
  - ローカルでビルドしたイメージをECRにプッシュ
  - EC2からECRにプルして実行
  - または、ローカルでビルドしたイメージを直接EC2に転送して実行も可能

### 2. EC2でのセットアップ手順（SSH接続後）

**現在の状態**: `[ec2-user@ip-172-31-40-83 ~]$` にログインできている

#### ステップ1: Pythonの確認とインストール

```bash
# Pythonのバージョンを確認
python3 --version

# Amazon Linux 2023の場合、Python 3.11がデフォルトで入っている可能性があります
# もし入っていない場合はインストール
sudo yum update -y
sudo yum install python3 python3-pip -y

# pipのバージョンを確認
pip3 --version
```

#### ステップ2: プロジェクトファイルの取得

**方法A: Gitリポジトリからクローン（推奨）**

```bash
# Gitがインストールされているか確認
git --version

# インストールされていない場合
sudo yum install git -y

# プロジェクトをクローン
cd ~
git clone <your-repo-url>
cd youtube-dashboard/backend/streamlit
```

**方法B: ローカルからscpで転送**

ローカルマシン（ターミナルを開いたまま）で実行：

```bash
# プロジェクトディレクトリに移動
cd /Users/nakazawa/Desktop/個人開発/youtube-dashboard

# EC2に転送（ディレクトリごと）
scp -i ~/.ssh/youtube-dashboard-key.pem -r backend ec2-user@54.238.232.151:~/
```

EC2側で：

```bash
# 転送されたファイルを確認
ls -la ~/backend
cd ~/backend/streamlit
```

#### ステップ3: 依存関係のインストール

```bash
# 現在のディレクトリを確認（backend/streamlitにいることを確認）
pwd

# 依存関係をインストール
pip3 install -r requirements.txt --user

# または、システム全体にインストール（sudoが必要）
sudo pip3 install -r requirements.txt
```

**インストール確認**:

```bash
# Streamlitがインストールされたか確認
streamlit --version
```

#### ステップ4: 環境変数の設定

```bash
# backendディレクトリに移動
cd ~/youtube-dashboard/backend
# または、scpで転送した場合は
cd ~/backend

# .envファイルを作成
nano .env
```

以下の内容を記述（RDSの情報に置き換えてください）：

```bash
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-password
DB_NAME=analytics
```

保存方法（nanoエディタ）:
- `Ctrl + O` で保存
- `Enter` で確認
- `Ctrl + X` で終了

#### ステップ5: Streamlitの起動（テスト）

```bash
# backendディレクトリにいることを確認
cd ~/youtube-dashboard/backend
# または
cd ~/backend

# Streamlitを起動
streamlit run streamlit/app.py --server.port=8501 --server.address=0.0.0.0
```

**接続確認**:
- ブラウザで `http://54.238.232.151:8501` にアクセス
- Streamlitアプリが表示されれば成功

**注意**: SSH接続を閉じるとStreamlitも停止します。バックグラウンドで実行する場合は次のステップ5を参照してください。

### 3. 環境変数の設定

```bash
# .envファイルを作成
cat > .env << EOF
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-password
DB_NAME=analytics
EOF
```

### 4. Streamlitの起動

```bash
cd ~/youtube-dashboard/backend
streamlit run streamlit/app.py --server.port=8501 --server.address=0.0.0.0
```

### 5. バックグラウンドで実行（systemdサービス）

```bash
# systemdサービスファイルを作成
sudo nano /etc/systemd/system/streamlit.service
```

以下の内容を記述：

```ini
[Unit]
Description=Streamlit Dashboard
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/youtube-dashboard/backend
Environment="DB_HOST=your-rds-endpoint.rds.amazonaws.com"
Environment="DB_USER=admin"
Environment="DB_PASSWORD=your-password"
Environment="DB_NAME=analytics"
ExecStart=/usr/bin/python3.11 -m streamlit run streamlit/app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

サービスを起動：

```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
sudo systemctl status streamlit
```

## Dockerでの実行

### 1. Dockerイメージのビルド

```bash
cd backend
docker build -t streamlit-app -f streamlit/Dockerfile .
```

### 2. Dockerコンテナの実行

**ローカルでの実行**:
```bash
docker run -d \
  -p 8501:8501 \
  -e DB_HOST=your-rds-endpoint.rds.amazonaws.com \
  -e DB_USER=admin \
  -e DB_PASSWORD=your-password \
  -e DB_NAME=analytics \
  --name streamlit-dashboard \
  streamlit-app
```

**EC2での実行（ECRを使用する場合）**:

1. **ECRリポジトリの作成**（オプション）:
   ```bash
   # AWS CLIでECRリポジトリを作成
   aws ecr create-repository --repository-name streamlit-app --region ap-northeast-1
   ```

2. **DockerイメージをECRにプッシュ**:
   ```bash
   # ECRにログイン
   aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com
   
   # イメージにタグを付ける
   docker tag streamlit-app:latest <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/streamlit-app:latest
   
   # ECRにプッシュ
   docker push <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/streamlit-app:latest
   ```

3. **EC2でECRからイメージをプルして実行**:
   ```bash
   # EC2インスタンスにSSH接続
   ssh -i your-key.pem ec2-user@your-ec2-ip
   
   # ECRにログイン
   aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com
   
   # イメージをプル
   docker pull <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/streamlit-app:latest
   
   # コンテナを実行
   docker run -d \
     -p 8501:8501 \
     -e DB_HOST=your-rds-endpoint.rds.amazonaws.com \
     -e DB_USER=admin \
     -e DB_PASSWORD=your-password \
     -e DB_NAME=analytics \
     --name streamlit-dashboard \
     <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/streamlit-app:latest
   ```

**EC2での実行（ECRを使わない場合）**:

ローカルでビルドしたイメージを直接EC2に転送することも可能です：

```bash
# ローカルでイメージをtarファイルに保存
docker save streamlit-app:latest | gzip > streamlit-app.tar.gz

# EC2に転送
scp -i your-key.pem streamlit-app.tar.gz ec2-user@your-ec2-ip:~/

# EC2でロード
ssh -i your-key.pem ec2-user@your-ec2-ip
docker load < streamlit-app.tar.gz

# コンテナを実行
docker run -d \
  -p 8501:8501 \
  -e DB_HOST=your-rds-endpoint.rds.amazonaws.com \
  -e DB_USER=admin \
  -e DB_PASSWORD=your-password \
  -e DB_NAME=analytics \
  --name streamlit-dashboard \
  streamlit-app:latest
```

### 3. ログの確認

```bash
docker logs streamlit-dashboard
```

### EC2とECRの関係まとめ

**EC2インスタンスの作成**:
- AWSコンソールの`EC2`サービスで作成
- 仮想サーバー（コンピューティングリソース）
- アプリケーションを実行する場所

**ECR（Elastic Container Registry）**:
- AWSコンソールの`ECR`サービスで作成
- Dockerコンテナイメージを保存するレジストリ（ストレージサービス）
- EC2でDockerを使う場合の**オプション**（必須ではない）

**使い分け**:
- **EC2で直接Pythonを実行**: EC2のみ必要、ECRは不要
- **EC2でDockerコンテナを実行**: EC2が必要、ECRはオプション（イメージの共有・管理に便利）
- **ECS Fargateで実行**: EC2は不要、ECRが必要（コンテナイメージを保存するため）

## トラブルシューティング

### データベース接続エラー

- RDSのセキュリティグループで、EC2からのアクセスを許可しているか確認
- 環境変数が正しく設定されているか確認
- RDSのエンドポイントが正しいか確認

### ポートが開いていない

- EC2のセキュリティグループでポート8501を開放
- ファイアウォール設定を確認

### モジュールが見つからない

- `backend`ディレクトリから実行しているか確認
- 依存関係が正しくインストールされているか確認

## 次のステップ

- ECS Fargateでのデプロイ（本番環境）
- Application Load Balancerの設定
- HTTPS対応（ACMで証明書を取得）

詳細は `README.md` と `STREAMLIT_AWS_ARCHITECTURE.md` を参照してください。


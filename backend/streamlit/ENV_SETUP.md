# 環境変数の設定方法

Streamlitアプリ用の環境変数を設定する方法は2つあります。

## 方法1: `.env.local`に追加（既存の設定と共有）

プロジェクトルート直下の`.env.local`に追加する場合：

```bash
# プロジェクトルートの .env.local に追加
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-password
DB_NAME=analytics
```

**メリット**:
- 既存の`.env.local`と共有できる
- 1つのファイルで管理できる

**注意点**:
- Next.js用の`NEXT_PUBLIC_API_BASE_URL`と混在する
- ルート直下のファイルなので、Streamlitアプリから見ると`../../.env.local`になる

## 方法2: `backend/.env`を作成（推奨）

バックエンド専用の`.env`ファイルを作成する場合：

```bash
# backend/.env を作成
cd backend
cat > .env << EOF
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-password
DB_NAME=analytics
EOF
```

**メリット**:
- バックエンド専用で管理できる
- フロントエンドの設定と分離できる
- Streamlitアプリから見やすい位置にある

**推奨**: この方法を推奨します。

## 環境変数の読み込み順序

Streamlitアプリは以下の順序で環境変数を読み込みます：

1. `backend/.env`（存在する場合、優先）
2. ルート直下の`.env.local`（フォールバック）
3. システムの環境変数

## 設定例

### `.env.local`に追加する場合

```bash
# プロジェクトルート/.env.local
# Next.js用
NEXT_PUBLIC_API_BASE_URL=https://abc123xyz.execute-api.ap-northeast-1.amazonaws.com

# Streamlit用（追加）
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-password
DB_NAME=analytics
```

### `backend/.env`を作成する場合

```bash
# backend/.env
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-password
DB_NAME=analytics
```

## 確認方法

環境変数が正しく読み込まれているか確認：

```bash
# Pythonで確認
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DB_HOST:', os.getenv('DB_HOST'))"
```

## 注意事項

- `.env`ファイルは`.gitignore`に含まれているため、Gitにコミットされません
- 機密情報（パスワードなど）が含まれるため、共有しないでください
- EC2やECS Fargateで実行する場合は、環境変数を直接設定するか、AWS Systems Manager Parameter StoreやSecrets Managerを使用してください



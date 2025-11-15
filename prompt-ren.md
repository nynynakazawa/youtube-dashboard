# YouTube チャンネル解析ダッシュボード - フロントエンド開発プロンプト（れん担当）

## プロジェクト概要

このプロジェクトは、YouTubeチャンネルの公開情報（動画一覧、視聴数、いいね数など）を自動取得し、ダッシュボードで可視化するシステムです。

**あなたの担当範囲：フロントエンド開発**
- React/Next.jsによるUI実装
- API Gateway（HTTP API）設定
- フロントエンドからのAPI呼び出し
- 簡易グラフ表示

**バックエンド担当：ざわ**
- AWS Lambda（Python）によるAPI実装
- RDSデータベース設計・実装
- DynamoDBによるキャッシュ制御
- YouTube Data API連携
- Streamlitによる分析ダッシュボード

---

## アーキテクチャ全体像

```
[ユーザー]
  │
  ▼
[React/Next.js]（あなたの担当）
  │ fetch()
  ▼
[API Gateway]（あなたが設定）
  │
  ▼
[Lambda (Python)]（ざわ担当）
  ├─ YouTube Data API
  ├─ DynamoDB（キャッシュ）
  └─ RDS（保存）
```

---

## コーディング規約（必須遵守）

このプロジェクトでは以下の原則に従ってコードを記述してください。

### 1. 宣言的なコード（Declarative Code）
- 命令的な実装（how）ではなく、何をしたいか（what）を明確に表現する
- 状態の変更は明示的に行い、副作用を最小限に抑える
- React/Next.jsでは、JSXで宣言的にUIを記述する
- ループ処理は`map`、`filter`、`reduce`などの関数型メソッドを使用
- 条件分岐は早期リターンや三項演算子を活用して可読性を向上させる

### 2. DRY原則（Don't Repeat Yourself）
- 同じロジックやコードの重複を避ける
- 3回以上使用されるコードは関数やコンポーネントとして抽出する
- 共通のユーティリティ関数は`utils/`または`lib/`ディレクトリに配置
- 再利用可能なコンポーネントは`components/`ディレクトリに配置
- 定数や設定値は`constants/`または`config/`に集約
- 型定義の重複を避け、共通の型は`types/`ディレクトリに配置

### 3. 拡張を見据えたコード設計
- 将来の機能追加や変更を考慮した柔軟な設計を心がける
- インターフェースや抽象化を適切に使用し、実装の詳細を隠蔽する
- 設定や環境変数は外部化し、ハードコーディングを避ける
- プラグインやモジュール化可能な構造を意識する
- 単一責任の原則（SRP）に従い、各モジュールは一つの責任のみを持つ
- 依存性の注入やファクトリーパターンを活用して結合度を下げる

### 4. 無駄なフォールバックはしない
- 不要なデフォルト値やフォールバック処理を追加しない
- エラーハンドリングは必要最小限に留める
- 過度なnullチェックやundefinedチェックは避ける（TypeScriptの型システムを活用）
- 実際にエラーが発生する可能性がある箇所のみエラーハンドリングを実装
- 不要なtry-catchブロックは使用しない
- オプショナルチェーン（`?.`）やnull合体演算子（`??`）は必要な場合のみ使用

### 5. 不要なコードやファイルの削除
- 使用されていないインポート、変数、関数、コンポーネントは削除する
- コメントアウトされたコードは削除する（Git履歴に残るため）
- 未使用のファイルやディレクトリは削除する
- デッドコードや到達不可能なコードは削除する
- リファクタリング後は古いコードを確実に削除する
- 一時的なデバッグコードやconsole.logは本番コードに残さない

### 6. 分かりやすいルール化された階層構造
- プロジェクトのディレクトリ構造は一貫性を保つ
- ファイル名は明確で一貫した命名規則に従う（`PascalCase` for components, `camelCase` for utilities）
- 関連するファイルは同じディレクトリに配置する
- ディレクトリ名は複数形を使用（例: `components/`, `utils/`, `types/`）
- 各ディレクトリの役割を明確に定義する

---

## ディレクトリ構造

```
app/                              # Next.js App Router
├── (routes)/                    # ルートグループ
│   ├── channels/               # チャンネル関連ページ
│   │   ├── [id]/              # 動的ルート
│   │   │   ├── page.tsx       # チャンネル詳細ページ
│   │   │   └── videos/        # 動画一覧ページ
│   │   │       └── page.tsx
│   │   └── import/            # チャンネル登録ページ
│   │       └── page.tsx
│   └── layout.tsx
├── components/                  # ページ固有のコンポーネント
├── layout.tsx                   # レイアウト
└── page.tsx                     # トップページ

components/                       # 再利用可能な共通コンポーネント
├── ui/                         # UIプリミティブコンポーネント
│   ├── Button.tsx
│   ├── Input.tsx
│   └── Card.tsx
└── features/                    # 機能別コンポーネント
    ├── channels/               # チャンネル関連
    │   ├── ChannelForm.tsx    # チャンネル登録フォーム
    │   └── ChannelCard.tsx    # チャンネルカード
    ├── videos/                 # 動画関連
    │   ├── VideoList.tsx       # 動画一覧
    │   ├── VideoCard.tsx       # 動画カード
    │   └── VideoFilters.tsx   # フィルター
    └── charts/                 # グラフ関連
        ├── TopVideosChart.tsx  # 再生数トップ10
        └── MonthlyViewsChart.tsx # 月別総再生数

lib/                             # ライブラリ設定や初期化
├── api.ts                      # API呼び出し関数
└── config.ts                   # 設定

utils/                           # ユーティリティ関数
├── format.ts                   # フォーマット関数
└── validation.ts               # バリデーション関数

types/                           # TypeScript型定義
├── channel.ts                  # チャンネル関連の型
├── video.ts                    # 動画関連の型
└── api.ts                      # APIレスポンスの型

constants/                       # 定数
└── config.ts                   # 設定値

hooks/                           # カスタムフック
├── useChannels.ts             # チャンネル取得フック
└── useVideos.ts               # 動画取得フック
```

---

## 命名規則

- **コンポーネント**: `PascalCase`（例: `UserProfile.tsx`）
- **関数・変数**: `camelCase`（例: `getUserData`）
- **定数**: `UPPER_SNAKE_CASE`（例: `API_BASE_URL`）
- **型・インターフェース**: `PascalCase`（例: `UserData`）
- **ファイル名**: コンポーネントは`PascalCase`、その他は`camelCase`

---

## インポート順序

1. 外部ライブラリ（React, Next.js等）
2. 内部モジュール（`@/components`, `@/utils`等）
3. 相対パスインポート
4. 型インポート（`import type`）

---

## 実装要件

### 1. チャンネル登録フォーム（POST /channels/import）

**ページ**: `app/(routes)/channels/import/page.tsx`

**機能:**
- チャンネルURLまたはchannelIdを入力するフォーム
- バリデーション（形式チェック）
- エラー表示
- ローディング状態の表示
- 成功時のリダイレクトまたは結果表示

**入力形式の例:**
- `https://www.youtube.com/@hoge`
- `https://www.youtube.com/channel/UCxxxxxx`
- `UCxxxxxxx`（純粋なchannelId）

**バリデーション:**
- 未入力 → エラーメッセージ「チャンネルURLまたはIDを入力してください」
- 形式チェック:
  - `youtube.com`を含むURLの場合 → 正規表現でchannelIdまたは@ハンドルを抽出
  - それ以外 → そのままchannelId候補としてAPIに送る

**API呼び出し:**
```typescript
POST /channels/import
Body: {
  channelUrlOrId: string
}
```

**レスポンス例:**
```typescript
{
  channel: {
    id: number
    youtubeChannelId: string
    title: string
    description: string
    publishedAt: string
    subscriberCount: number
    videoCount: number
    viewCount: number
  }
  summary: {
    totalViews: number
    totalVideos: number
    lastFetchedAt: string
  }
}
```

**エラーハンドリング:**
- 400: パラメータ不正 → 「チャンネルID抽出に失敗しました」
- 404: チャンネルが見つからない → 「指定されたチャンネルが見つかりませんでした」
- 429: 更新間隔制限 → 「短時間に更新しすぎです。しばらく待ってから再度お試しください」
- 500: 内部エラー → 「サーバーエラーが発生しました。しばらく待ってから再度お試しください」

### 2. 動画一覧表示（GET /channels/{id}/videos）

**ページ**: `app/(routes)/channels/[id]/videos/page.tsx`

**機能:**
- 動画一覧の表示
- ソート機能（投稿日時、再生数、高評価数、コメント数）
- フィルタ機能（期間指定、最低再生数）
- ページング（1ページあたり20件）

**表示項目:**
- サムネイル画像（クリックでYouTubeに飛ぶ）
- 動画タイトル
- 投稿日時
- 再生数
- 高評価数
- コメント数
- 長さ（秒 → mm:ss表示）

**ソート条件:**
- 投稿日時（降順/昇順）
- 再生数（降順/昇順）
- 高評価数（降順/昇順）
- コメント数（降順/昇順）

**フィルタ:**
- 投稿日時の期間指定（開始日〜終了日）
- 最低再生数（例：1万回以上）

**API呼び出し:**
```typescript
GET /channels/{id}/videos?sort=views_desc&limit=20&offset=0&from=2024-01-01&to=2025-01-01&minViews=10000
```

**レスポンス例:**
```typescript
{
  items: [
    {
      id: number
      youtubeVideoId: string
      title: string
      thumbnailUrl: string
      publishedAt: string
      durationSec: number
      latestStats: {
        viewCount: number
        likeCount: number
        commentCount: number
      }
    }
  ]
  totalCount: number
}
```

### 3. 簡易グラフ表示

**コンポーネント**: `components/features/charts/`

#### 3.1 再生数トップ10のバーグラフ

**コンポーネント**: `TopVideosChart.tsx`

**仕様:**
- X軸: 動画タイトル（またはタイトルの短縮形）
- Y軸: 再生数
- 動画一覧APIから取得したデータを使用

#### 3.2 月別総再生数推移

**コンポーネント**: `MonthlyViewsChart.tsx`

**仕様:**
- X軸: 年月
- Y軸: その月に公開された動画の再生数合計（最新statsベース）
- 動画一覧APIから取得したデータを集計して使用

**グラフライブラリ:**
- RechartsまたはChart.jsを使用（任意）

### 4. API Gateway設定

**種別**: AWS API Gateway HTTP API（v2）

**設定内容:**
- `/channels/import` → Lambda（ざわの関数）に紐づけ
- `/channels` → Lambda（ざわの関数）に紐づけ
- `/channels/{id}` → Lambda（ざわの関数）に紐づけ
- `/channels/{id}/videos` → Lambda（ざわの関数）に紐づけ

**CORS設定:**
- Allow Origin: ReactのCloudFrontドメイン
- メソッド: GET, POST, OPTIONS
- ヘッダ: Content-Type, Authorization

**注意**: API Gateway自体にプログラムを書かず、設定のみ

### 5. インフラ設定（AWS）

**S3バケット:**
- 静的ウェブホスティング用
- バージョニング有効化推奨

**CloudFront:**
- オリジン: 上記S3バケット
- HTTPS有効（ACMで証明書）
- キャッシュポリシー:
  - HTML: 短め（数分）
  - JS/CSS: 長め（ハッシュつきファイル名前提）

---

## 型定義

### チャンネル関連の型

```typescript
// types/channel.ts
export interface Channel {
  id: number
  youtubeChannelId: string
  title: string
  description: string
  publishedAt: string
  subscriberCount: number
  videoCount: number
  viewCount: number
}

export interface ChannelSummary {
  totalViews: number
  totalVideos: number
  lastFetchedAt: string
}

export interface ChannelImportResponse {
  channel: Channel
  summary: ChannelSummary
}
```

### 動画関連の型

```typescript
// types/video.ts
export interface VideoStats {
  viewCount: number
  likeCount: number
  commentCount: number
}

export interface Video {
  id: number
  youtubeVideoId: string
  title: string
  thumbnailUrl: string
  publishedAt: string
  durationSec: number
  latestStats: VideoStats
}

export interface VideoListResponse {
  items: Video[]
  totalCount: number
}
```

---

## API呼び出し関数

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || ''

// チャンネルを登録・インポート（POST /channels/import）
export async function importChannel(channelUrlOrId: string): Promise<ChannelImportResponse> {
  const response = await fetch(`${API_BASE_URL}/channels/import`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ channelUrlOrId }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error?.message || 'チャンネルのインポートに失敗しました')
  }

  return response.json()
}

// チャンネル一覧を取得（GET /channels）
export async function getChannels(params?: {
  q?: string
  limit?: number
  offset?: number
}): Promise<{ items: Channel[]; totalCount: number }> {
  const queryParams = new URLSearchParams()
  if (params?.q) queryParams.set('q', params.q)
  if (params?.limit) queryParams.set('limit', params.limit.toString())
  if (params?.offset) queryParams.set('offset', params.offset.toString())

  const response = await fetch(`${API_BASE_URL}/channels?${queryParams}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error?.message || 'チャンネル一覧の取得に失敗しました')
  }

  return response.json()
}

// チャンネル詳細を取得（GET /channels/{id}）
export async function getChannel(channelId: number): Promise<ChannelImportResponse> {
  const response = await fetch(`${API_BASE_URL}/channels/${channelId}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error?.message || 'チャンネル詳細の取得に失敗しました')
  }

  return response.json()
}

// チャンネルの動画一覧を取得（GET /channels/{id}/videos）
export async function getChannelVideos(
  channelId: number,
  params?: {
    sort?: string
    limit?: number
    offset?: number
    from?: string
    to?: string
    minViews?: number
  }
): Promise<VideoListResponse> {
  const queryParams = new URLSearchParams()
  if (params?.sort) queryParams.set('sort', params.sort)
  if (params?.limit) queryParams.set('limit', params.limit.toString())
  if (params?.offset) queryParams.set('offset', params.offset.toString())
  if (params?.from) queryParams.set('from', params.from)
  if (params?.to) queryParams.set('to', params.to)
  if (params?.minViews) queryParams.set('minViews', params.minViews.toString())

  const response = await fetch(`${API_BASE_URL}/channels/${channelId}/videos?${queryParams}`)
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error?.message || '動画一覧の取得に失敗しました')
  }

  return response.json()
}
```

---

## 環境変数

```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=https://{api-id}.execute-api.{region}.amazonaws.com/prod
```

---

## React/Next.jsのベストプラクティス

### Server Componentsを優先
- デフォルトでServer Componentsを使用
- クライアントコンポーネントは必要な場合のみ（`'use client'`）

### カスタムフックでロジックを分離
- API呼び出しロジックはカスタムフックに分離
- 状態管理もカスタムフックで抽象化

### パフォーマンス最適化
- `useMemo`、`useCallback`は必要な場合のみ使用
- 画像はNext.js Imageコンポーネントを使用
- コード分割を適切に使用

### エラーハンドリング
- エラーは適切なレベルでキャッチし、ユーザーに分かりやすいメッセージを表示
- エラーバウンダリーを適切に配置

---

## 開発手順

1. **Step1**: ReactでチャンネルID入力フォームを作成
   - POST /channels/importを叩けるようにする
   - バックエンドがダミーJSONを返す段階でも動作するようにする

2. **Step2**: 動画一覧ページを作成
   - GET /channels/{id}/videosを呼び出す
   - ソート・フィルタ機能を実装

3. **Step3**: 簡易グラフを実装
   - 再生数トップ10のバーグラフ
   - 月別総再生数の推移グラフ

4. **Step4**: API Gateway設定
   - ルーティング設定
   - CORS設定

5. **Step5**: S3 + CloudFront設定
   - 静的ホスティング設定
   - デプロイパイプライン構築

---

## 完成像

- モダンなフロントエンドとAPI Gatewayの運用構築経験
- React/Next.jsによる宣言的なUI実装
- 型安全なAPI連携
- インターンでもそのまま提出できるレベルの本物プロダクト


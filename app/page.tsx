import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-semibold text-gray-900 sm:text-3xl">YouTube チャンネル解析ダッシュボード</h1>
        <p className="mt-2 text-sm text-gray-500 sm:text-base">
          チャンネルの成長や動画のパフォーマンスを可視化するためのダッシュボードです。
        </p>
      </section>

      <section className="grid gap-8 grid-cols-1 md:grid-cols-2">
        <article className="modern-card">
          <div className="card-inner">
            <span className="card-pricing">
              <span>新規</span>
            </span>
            <p className="card-title">チャンネルを登録</p>
            <p className="card-info">
              YouTubeチャンネルを登録して、動画のパフォーマンスを分析できます。
            </p>
            <ul className="card-features">
              <li>
                <span className="icon">
                  <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 0h24v24H0z" fill="none"></path>
                    <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                  </svg>
                </span>
                <span>チャンネル情報の自動取得</span>
              </li>
              <li>
                <span className="icon">
                  <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 0h24v24H0z" fill="none"></path>
                    <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                  </svg>
                </span>
                <span>動画データの分析</span>
              </li>
              <li>
                <span className="icon">
                  <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 0h24v24H0z" fill="none"></path>
                    <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                  </svg>
                </span>
                <span>パフォーマンス可視化</span>
              </li>
            </ul>
            <div className="card-action">
              <Link href="/channels/import" className="card-button">
                チャンネルを取り込む
              </Link>
            </div>
          </div>
        </article>

        <article className="modern-card">
          <div className="card-inner">
            <span className="card-pricing">
              <span>一覧</span>
            </span>
            <p className="card-title">チャンネル一覧</p>
            <p className="card-info">
              登録済みのチャンネル一覧を確認し、詳細情報や動画一覧を閲覧できます。
            </p>
            <ul className="card-features">
              <li>
                <span className="icon">
                  <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 0h24v24H0z" fill="none"></path>
                    <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                  </svg>
                </span>
                <span>登録済みチャンネルの確認</span>
              </li>
              <li>
                <span className="icon">
                  <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 0h24v24H0z" fill="none"></path>
                    <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                  </svg>
                </span>
                <span>詳細情報の閲覧</span>
              </li>
              <li>
                <span className="icon">
                  <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0 0h24v24H0z" fill="none"></path>
                    <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                  </svg>
                </span>
                <span>動画一覧へのアクセス</span>
              </li>
            </ul>
            <div className="card-action">
              <Link href="/channels" className="card-button">
                チャンネル一覧を見る
              </Link>
            </div>
          </div>
        </article>
      </section>
    </div>
  );
}

import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-semibold text-gray-900">YouTube チャンネル解析ダッシュボード</h1>
        <p className="mt-2 text-sm text-gray-500">
          チャンネルの成長や動画のパフォーマンスを可視化するためのダッシュボードです。
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <article className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">チャンネルを登録</h2>
          <p className="mt-2 text-sm text-gray-500">
            YouTubeチャンネルを登録して、動画のパフォーマンスを分析できます。
          </p>
          <Link
            href="/channels/import"
            className="mt-4 inline-flex items-center justify-center rounded-full bg-youtube-red px-5 py-2 text-sm font-semibold text-white transition hover:bg-red-600"
          >
            チャンネルを取り込む
          </Link>
        </article>

        <article className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">チャンネル一覧</h2>
          <p className="mt-2 text-sm text-gray-500">
            登録済みのチャンネル一覧を確認し、詳細情報や動画一覧を閲覧できます。
          </p>
          <Link
            href="/channels"
            className="mt-4 inline-flex items-center justify-center rounded-full border border-gray-200 px-5 py-2 text-sm font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red"
          >
            チャンネル一覧を見る
          </Link>
        </article>
      </section>
    </div>
  );
}

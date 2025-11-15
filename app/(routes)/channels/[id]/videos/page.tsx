import Link from "next/link";

type PageProps = {
  params: { id: string };
};

const videos = [
  {
    id: "vid-001",
    title: "ショート動画撮影術まとめ",
    publishedAt: "2025/11/10",
    views: "156K",
    likes: "6.1K",
    comments: "482",
    duration: "08:12",
  },
  {
    id: "vid-002",
    title: "ライブ配信の裏側 Q&A",
    publishedAt: "2025/11/07",
    views: "92K",
    likes: "3.4K",
    comments: "210",
    duration: "52:44",
  },
  {
    id: "vid-003",
    title: "週末VLOG #58 - 秋の撮影会",
    publishedAt: "2025/11/04",
    views: "64K",
    likes: "2.1K",
    comments: "134",
    duration: "12:56",
  },
];

export default function ChannelVideosPage({ params }: PageProps) {
  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-sm uppercase tracking-wide text-gray-500">channels / {params.id} / videos</p>
        <h1 className="text-2xl font-semibold text-gray-900">動画一覧</h1>
        <p className="text-sm text-gray-500">
          バックエンドの `getChannelVideos` API を想定したテーブルレイアウトです。ソートやフィルター UI もプレースホルダーとして
          用意しています。
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/channels/${params.id}`}
            className="inline-flex items-center justify-center rounded-full border border-gray-200 px-5 py-2 text-sm font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red"
          >
            チャンネル詳細に戻る
          </Link>
          <Link
            href="/channels"
            className="inline-flex items-center justify-center rounded-full border border-gray-200 px-5 py-2 text-sm font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red"
          >
            一覧へ戻る
          </Link>
        </div>
      </header>

      <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="grid gap-4 lg:grid-cols-3">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-gray-500">並び替え</label>
            <select className="mt-2 w-full rounded-xl border border-gray-200 px-4 py-2 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20">
              <option>再生数（降順）</option>
              <option>再生数（昇順）</option>
              <option>投稿日（新しい順）</option>
              <option>投稿日（古い順）</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-gray-500">期間フィルター</label>
            <div className="mt-2 flex gap-3">
              <input
                type="date"
                className="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              />
              <input
                type="date"
                className="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              />
            </div>
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-gray-500">最低再生数</label>
            <input
              type="number"
              placeholder="例: 1000"
              className="mt-2 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
            />
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-gray-100 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-100 text-sm">
            <thead className="bg-gray-50 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
              <tr>
                <th className="px-4 py-3">動画タイトル</th>
                <th className="px-4 py-3">公開日</th>
                <th className="px-4 py-3">再生数</th>
                <th className="px-4 py-3">高評価</th>
                <th className="px-4 py-3">コメント</th>
                <th className="px-4 py-3">尺</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white text-gray-700">
              {videos.map((video) => (
                <tr key={video.id} className="transition hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <p className="font-semibold text-gray-900">{video.title}</p>
                    <p className="text-xs text-gray-500">ID: {video.id}</p>
                  </td>
                  <td className="px-4 py-3">{video.publishedAt}</td>
                  <td className="px-4 py-3">{video.views}</td>
                  <td className="px-4 py-3">{video.likes}</td>
                  <td className="px-4 py-3">{video.comments}</td>
                  <td className="px-4 py-3">{video.duration}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

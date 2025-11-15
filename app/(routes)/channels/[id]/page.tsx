import Link from "next/link";

type PageProps = {
  params: { id: string };
};

const metrics = [
  { label: "直近30日再生数", value: "1.2M", delta: "+8.5%" },
  { label: "登録者の増加", value: "+12,430", delta: "+5.1%" },
  { label: "平均視聴時間", value: "5分42秒", delta: "+0.8%" },
];

export default function ChannelDetailPage({ params }: PageProps) {
  const channelName = params.id === "demo" ? "YouTube Demo Channel" : `Channel: ${params.id}`;

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-sm uppercase tracking-wide text-gray-500">channels / {params.id}</p>
        <h1 className="text-2xl font-semibold text-gray-900">{channelName}</h1>
        <p className="text-sm text-gray-500">
          ここではバックエンドから取得したチャンネルサマリを表示します。現在はダミーデータですが、
          `lib/api.ts` の `getChannel` と結合する想定で UI を準備しています。
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/channels/${params.id}/videos`}
            className="inline-flex items-center justify-center rounded-full bg-youtube-red px-5 py-2 text-sm font-semibold text-white transition hover:bg-red-600"
          >
            動画一覧を開く
          </Link>
          <Link
            href="/channels"
            className="inline-flex items-center justify-center rounded-full border border-gray-200 px-5 py-2 text-sm font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red"
          >
            チャンネル一覧に戻る
          </Link>
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-3">
        {metrics.map((metric) => (
          <article key={metric.label} className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{metric.label}</p>
            <p className="mt-3 text-2xl font-semibold text-gray-900">{metric.value}</p>
            <p className="mt-1 text-xs font-semibold text-emerald-500">{metric.delta}</p>
          </article>
        ))}
      </section>

      <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">視聴動向（モック）</h2>
            <p className="text-sm text-gray-500">
              Recharts でグラフを描画する予定のプレースホルダーです。バックエンドの `/stats/summary` エンドポイントと接続します。
            </p>
          </div>
          <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold text-gray-500">準備中</span>
        </div>
        <div className="mt-6 rounded-xl border border-dashed border-gray-200 bg-gray-50 p-6 text-center text-sm text-gray-500">
          グラフコンポーネントがここに入ります。データモデルが整い次第、TopVideosChart / MonthlyViewsChart を配置してください。
        </div>
      </section>
    </div>
  );
}

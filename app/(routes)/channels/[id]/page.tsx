import Link from "next/link";

import { getChannel, getChannelVideos } from "@/lib/api";
import { formatNumber } from "@/utils/format";
import TopVideosChart from "@/components/features/charts/TopVideosChart";
import MonthlyViewsChart from "@/components/features/charts/MonthlyViewsChart";
import type { PageProps } from "@/types/page";
import type { ChannelMetric } from "@/types/dashboard";
import type { Video } from "@/types/video";

export default async function ChannelDetailPage({ params }: PageProps) {
  // Next.js 15ではparamsがPromiseになる可能性があるため、awaitする
  const resolvedParams = await params;
  const channelId = parseInt(resolvedParams.id, 10);
  let channelName = `Channel: ${resolvedParams.id}`;
  let metrics: ChannelMetric[] = [];
  let error: string | null = null;
  let videos: Video[] = [];

  if (isNaN(channelId)) {
    error = "無効なチャンネルIDです";
  } else {
    try {
      const response = await getChannel(channelId);
      channelName = response.channel.title;
      metrics = [
        {
          label: "総再生回数",
          value: formatNumber(response.channel.viewCount),
          delta: "-",
        },
        {
          label: "登録者数",
          value: formatNumber(response.channel.subscriberCount),
          delta: "-",
        },
        {
          label: "動画数",
          value: `${response.channel.videoCount}本`,
          delta: "-",
        },
      ];

      // グラフ用に動画データを取得
      try {
        const videosResponse = await getChannelVideos(channelId, { sort: "views_desc", limit: 100 });
        videos = videosResponse.items;
      } catch (videoErr) {
        // 動画データの取得に失敗してもエラーにはしない（グラフを表示しないだけ）
        console.error("動画データの取得に失敗しました:", videoErr);
      }
    } catch (err) {
      error = err instanceof Error ? err.message : "チャンネル情報の取得に失敗しました";
    }
  }

  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-sm uppercase tracking-wide text-gray-500">channels / {resolvedParams.id}</p>
        <h1 className="text-2xl font-semibold text-gray-900">{channelName}</h1>
        <p className="text-sm text-gray-500">
          ここではバックエンドから取得したチャンネルサマリを表示します。
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/channels/${resolvedParams.id}/videos`}
            className="btn-glass-primary"
          >
            動画一覧を開く
          </Link>
          <Link
            href="/channels"
            className="btn-glass"
          >
            チャンネル一覧に戻る
          </Link>
        </div>
      </header>

      {error ? (
        <div className="modern-card">
          <div className="card-inner">
            <div className="p-6 text-center">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid gap-8 grid-cols-1 md:grid-cols-2">
          <section className="grid gap-6 grid-cols-1">
            {metrics.map((metric) => (
              <article key={metric.label} className="metric-card">
                <div className="metric-inner">
                  <span className="metric-badge">
                    {metric.label}
                  </span>
                  <p className="metric-value">{metric.value}</p>
                  {metric.delta !== "-" && (
                    <p className="mt-2 text-xs font-semibold text-emerald-500">{metric.delta}</p>
                  )}
                </div>
              </article>
            ))}
          </section>

          <section className="modern-card">
            <div className="card-inner">
              <div className="mb-6">
                <h2 className="card-title">視聴動向</h2>
                <p className="card-info">
                  チャンネルの動画データを可視化しています。
                </p>
              </div>

              {videos.length > 0 ? (
                <div className="space-y-8">
                  <div>
                    <h3 className="mb-4 text-base font-semibold text-gray-900">再生数トップ10</h3>
                    <TopVideosChart videos={videos} />
                  </div>
                  <div>
                    <h3 className="mb-4 text-base font-semibold text-gray-900">月別総再生数推移</h3>
                    <MonthlyViewsChart videos={videos} />
                  </div>
                </div>
              ) : (
                <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-gray-200 bg-gray-50 text-sm text-gray-500">
                  動画データがありません
                </div>
              )}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

import { notFound } from "next/navigation";
import Link from "next/link";
import { getChannel } from "@/lib/api";
import type { ChannelImportResponse } from "@/types/channel";

interface ChannelDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function ChannelDetailPage({
  params,
}: ChannelDetailPageProps) {
  const { id } = await params;
  const channelId = parseInt(id, 10);

  if (isNaN(channelId)) {
    notFound();
  }

  let channelData: ChannelImportResponse;
  try {
    channelData = await getChannel(channelId);
  } catch (error) {
    notFound();
  }

  const { channel, summary } = channelData;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{channel.title}</h1>
        <p className="mt-2 text-sm text-gray-500">{channel.description}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
            登録者数
          </p>
          <p className="mt-3 text-2xl font-semibold text-gray-900">
            {channel.subscriberCount.toLocaleString()}
          </p>
        </div>
        <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
            公開動画数
          </p>
          <p className="mt-3 text-2xl font-semibold text-gray-900">
            {channel.videoCount.toLocaleString()}
          </p>
        </div>
        <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
            総再生数
          </p>
          <p className="mt-3 text-2xl font-semibold text-gray-900">
            {channel.viewCount.toLocaleString()}
          </p>
        </div>
        <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
            最終取得日時
          </p>
          <p className="mt-3 text-sm font-semibold text-gray-900">
            {new Date(summary.lastFetchedAt).toLocaleString("ja-JP")}
          </p>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">動画一覧</h2>
            <p className="mt-1 text-sm text-gray-500">
              合計 {summary.totalVideos} 本の動画
            </p>
          </div>
          <Link
            href={`/channels/${channelId}/videos`}
            className="rounded-full border border-gray-200 px-4 py-2 text-xs font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red"
          >
            すべて表示
          </Link>
        </div>
      </div>
    </div>
  );
}


import Link from "next/link";

import { getChannels } from "@/lib/api";
import { formatChannelListItem } from "@/utils/format";
import type { ChannelListItem } from "@/types/channel";

export default async function ChannelsPage() {
  let channels: ChannelListItem[] = [];
  let error: string | null = null;

  try {
    const response = await getChannels();
    channels = response.items.map(formatChannelListItem);
  } catch (err) {
    error = err instanceof Error ? err.message : "チャンネル一覧の取得に失敗しました";
  }
  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-sm uppercase tracking-wide text-gray-500">channels</p>
        <h1 className="text-2xl font-semibold text-gray-900">登録済みチャンネル</h1>
        <p className="text-sm text-gray-500">
          ここではインポート済みのチャンネル一覧を表示します。各行をクリックするとチャンネル詳細、右側のアクションから動画一覧に
          遷移できます。
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/channels/import"
            className="inline-flex items-center justify-center rounded-full bg-youtube-red px-5 py-2 text-sm font-semibold text-white transition hover:bg-red-600"
          >
            新規チャンネルを取り込む
          </Link>
          <Link
            href="/channels/demo"
            className="inline-flex items-center justify-center rounded-full border border-gray-200 px-5 py-2 text-sm font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red"
          >
            デモチャンネルを表示
          </Link>
        </div>
      </header>

      <section className="rounded-2xl border border-gray-100 bg-white shadow-sm">
        {error ? (
          <div className="p-6 text-center">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : channels.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-sm text-gray-500">登録済みのチャンネルがありません</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 text-sm">
              <thead className="bg-gray-50 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                <tr>
                  <th className="px-4 py-3">チャンネル</th>
                  <th className="px-4 py-3">登録者数</th>
                  <th className="px-4 py-3">総再生回数</th>
                  <th className="px-4 py-3">動画数</th>
                  <th className="px-4 py-3">最終取得</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white text-gray-700">
                {channels.map((channel) => (
                  <tr key={channel.id} className="transition hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <Link
                        href={`/channels/${channel.id}`}
                        className="font-semibold text-gray-900 transition hover:text-youtube-red"
                      >
                        {channel.name}
                      </Link>
                    </td>
                    <td className="px-4 py-3">{channel.subscribers}</td>
                    <td className="px-4 py-3">{channel.totalViews}</td>
                    <td className="px-4 py-3">{channel.videos}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">{channel.lastFetched}</td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        href={`/channels/${channel.id}/videos`}
                        className="text-sm font-semibold text-youtube-red transition hover:text-red-600"
                      >
                        動画一覧
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
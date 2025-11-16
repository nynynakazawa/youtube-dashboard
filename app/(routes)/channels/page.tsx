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
            className="btn-glass-primary"
          >
            新規チャンネルを取り込む
          </Link>
          <Link
            href="/channels/demo"
            className="btn-glass"
          >
            デモチャンネルを表示
          </Link>
        </div>
      </header>

      <section>
        {error ? (
          <div className="modern-card">
            <div className="card-inner">
              <div className="p-6 text-center">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          </div>
        ) : channels.length === 0 ? (
          <div className="modern-card">
            <div className="card-inner">
              <div className="p-6 text-center">
                <p className="text-sm text-gray-500">登録済みのチャンネルがありません</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid gap-8 grid-cols-1 md:grid-cols-2">
            {channels.map((channel) => (
              <div key={channel.id} className="channel-card">
                <div className="channel-inner">
                  <Link
                    href={`/channels/${channel.id}`}
                    className="channel-title block transition hover:text-youtube-red"
                  >
                    {channel.name}
                  </Link>
                  <div className="channel-stats">
                    <div className="channel-stat">
                      <span className="icon">
                        <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M0 0h24v24H0z" fill="none"></path>
                          <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                        </svg>
                      </span>
                      <span>登録者数: <strong>{channel.subscribers}</strong></span>
                    </div>
                    <div className="channel-stat">
                      <span className="icon">
                        <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M0 0h24v24H0z" fill="none"></path>
                          <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                        </svg>
                      </span>
                      <span>総再生回数: <strong>{channel.totalViews}</strong></span>
                    </div>
                    <div className="channel-stat">
                      <span className="icon">
                        <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M0 0h24v24H0z" fill="none"></path>
                          <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                        </svg>
                      </span>
                      <span>動画数: <strong>{channel.videos}</strong></span>
                    </div>
                    <div className="channel-stat">
                      <span className="text-xs text-gray-500">最終取得: {channel.lastFetched}</span>
                    </div>
                  </div>
                  <div className="card-action mt-4">
                    <Link
                      href={`/channels/${channel.id}/videos`}
                      className="card-button text-center"
                    >
                      動画一覧を見る
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
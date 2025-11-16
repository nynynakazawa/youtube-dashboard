"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { importChannel, getChannels } from "@/lib/api";
import { formatChannelListItem } from "@/utils/format";
import type { ChannelListItem } from "@/types/channel";

export default function ChannelImportPage() {
  const router = useRouter();
  const [channelUrlOrId, setChannelUrlOrId] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recentChannels, setRecentChannels] = useState<ChannelListItem[]>([]);
  const [isLoadingChannels, setIsLoadingChannels] = useState(true);
  const [channelsError, setChannelsError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecentChannels = async () => {
      try {
        const response = await getChannels({ limit: 5 });
        setRecentChannels(response.items.map(formatChannelListItem));
        setChannelsError(null);
      } catch (err) {
        setChannelsError(
          err instanceof Error ? err.message : "チャンネル一覧の取得に失敗しました"
        );
      } finally {
        setIsLoadingChannels(false);
      }
    };

    fetchRecentChannels();
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!channelUrlOrId.trim()) {
      setError("チャンネルURLまたはIDを入力してください");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await importChannel(channelUrlOrId.trim());
      router.push(`/channels/${response.channel.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "チャンネルの取り込みに失敗しました");
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <h1 className="text-2xl font-semibold text-gray-900">チャンネルを取り込む</h1>
        <p className="text-sm text-gray-500">
          バックエンドで用意された API を利用してチャンネル情報を取り込みます。URL または ID を入力し、取り込みボタンを押すだけで
          即座に分析ビューへ反映されます。
        </p>
      </header>

      <section className="modern-card">
        <div className="card-inner">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="channelInput" className="text-sm font-semibold text-gray-800">
                チャンネル URL / ID
              </label>
              <input
                id="channelInput"
                type="text"
                value={channelUrlOrId}
                onChange={(e) => setChannelUrlOrId(e.target.value)}
                placeholder="https://www.youtube.com/@example または UCxxxx"
                className="glass-input-form w-full border border-white/30 bg-white/40 backdrop-blur-md text-sm text-gray-800 placeholder:text-gray-500/70 shadow-inner focus:border-white/50 focus:bg-white/60 focus:outline-none focus:ring-2 focus:ring-white/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
                disabled={isLoading}
              />
            </div>
            {error && (
              <div className="rounded-2xl bg-red-50 p-3 text-sm text-red-600">
                {error}
              </div>
            )}
            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="submit"
                disabled={isLoading || !channelUrlOrId.trim()}
                className="btn-glass-primary disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {isLoading ? "取り込み中..." : "取り込み"}
              </button>
              <Link
                href="/channels"
                className="btn-glass"
              >
                チャンネル一覧を見る
              </Link>
            </div>
          </form>
        </div>
      </section>

      <section className="modern-card">
        <div className="card-inner">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">最近登録されたチャンネル</h2>
            <p className="text-sm text-gray-500">最新5件のチャンネルを表示しています。</p>
          </div>
          <Link
            href="/channels"
            className="text-sm font-semibold text-youtube-red transition hover:text-red-600"
          >
            すべて表示
          </Link>
        </div>
        {isLoadingChannels ? (
          <div className="mt-6 p-6 text-center">
            <p className="text-sm text-gray-500">読み込み中...</p>
          </div>
        ) : channelsError ? (
          <div className="mt-6 p-6 rounded-2xl bg-red-50 border border-red-200">
            <p className="text-sm font-semibold text-red-800 mb-2">エラーが発生しました</p>
            <pre className="text-xs text-red-700 whitespace-pre-wrap break-words bg-red-100 p-3 rounded-2xl border border-red-200">
              {channelsError}
            </pre>
            <div className="mt-4 space-y-2 text-left text-xs text-gray-600">
              <p className="font-semibold text-gray-800">トラブルシューティング:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>ブラウザの開発者ツール（F12）のコンソールタブでCORSエラーを確認</li>
                <li>API GatewayのCORS設定で <code className="bg-gray-100 px-1 rounded">http://localhost:3000</code> が許可されているか確認</li>
                <li>API Gatewayがデプロイされているか確認</li>
                <li>ネットワークタブでリクエストの詳細を確認</li>
              </ul>
            </div>
          </div>
        ) : recentChannels.length === 0 ? (
          <div className="mt-6 p-6 text-center">
            <p className="text-sm text-gray-500">登録済みのチャンネルがありません</p>
          </div>
        ) : (
          <div className="mt-6 grid gap-8 grid-cols-1 md:grid-cols-2">
            {recentChannels.map((channel) => (
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
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        </div>
      </section>
    </div>
  );
}
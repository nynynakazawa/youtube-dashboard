"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getChannels } from "@/lib/api";
import type { Channel } from "@/types/channel";

const ITEMS_PER_PAGE = 20;

export default function ChannelsPage() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const fetchChannels = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getChannels({
          q: searchQuery || undefined,
          limit: ITEMS_PER_PAGE,
          offset: (currentPage - 1) * ITEMS_PER_PAGE,
        });
        setChannels(data.items);
        setTotalCount(data.totalCount);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "チャンネル一覧の取得に失敗しました"
        );
      } finally {
        setIsLoading(false);
      }
    };

    const timeoutId = setTimeout(() => {
      fetchChannels();
    }, searchQuery ? 300 : 0);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, currentPage]);

  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">チャンネル一覧</h1>
        <p className="mt-2 text-sm text-gray-500">
          合計 {totalCount} 件のチャンネル
        </p>
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="mb-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            placeholder="チャンネルを検索"
            className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
          />
        </div>

        {error && (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">読み込み中...</p>
          </div>
        ) : channels.length === 0 ? (
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">チャンネルが見つかりませんでした</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                      タイトル
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                      登録者数
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                      総再生数
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
                      動画数
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {channels.map((channel) => (
                    <tr
                      key={channel.id}
                      className="border-b border-gray-100 transition hover:bg-gray-50"
                    >
                      <td className="px-4 py-4">
                        <Link
                          href={`/channels/${channel.id}`}
                          className="font-semibold text-gray-900 hover:text-youtube-red"
                        >
                          {channel.title}
                        </Link>
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-600">
                        {channel.subscriberCount.toLocaleString()}
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-600">
                        {channel.viewCount.toLocaleString()}
                      </td>
                      <td className="px-4 py-4 text-sm text-gray-600">
                        {channel.videoCount.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="mt-6 flex items-center justify-center gap-2">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="rounded-xl border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  前へ
                </button>
                <span className="text-sm text-gray-600">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() =>
                    setCurrentPage((p) => Math.min(totalPages, p + 1))
                  }
                  disabled={currentPage === totalPages}
                  className="rounded-xl border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  次へ
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}


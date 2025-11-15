"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

import { getChannelVideos } from "@/lib/api";
import { formatVideoListItem } from "@/utils/format";
import type { PageProps } from "@/types/page";
import type { VideoListItem } from "@/types/video";

export default function ChannelVideosPage({ params }: PageProps) {
  const channelId = parseInt(params.id, 10);
  const [videos, setVideos] = useState<VideoListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sort, setSort] = useState("views_desc");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [minViews, setMinViews] = useState("");

  useEffect(() => {
    if (isNaN(channelId)) {
      setError("無効なチャンネルIDです");
      setIsLoading(false);
      return;
    }

    const fetchVideos = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const params: {
          sort?: string;
          from?: string;
          to?: string;
          minViews?: number;
        } = {};

        if (sort) {
          params.sort = sort;
        }
        if (fromDate) {
          params.from = fromDate;
        }
        if (toDate) {
          params.to = toDate;
        }
        if (minViews) {
          params.minViews = parseInt(minViews, 10);
        }

        const response = await getChannelVideos(channelId, params);
        setVideos(response.items.map(formatVideoListItem));
      } catch (err) {
        setError(err instanceof Error ? err.message : "動画一覧の取得に失敗しました");
      } finally {
        setIsLoading(false);
      }
    };

    fetchVideos();
  }, [channelId, sort, fromDate, toDate, minViews]);
  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-sm uppercase tracking-wide text-gray-500">channels / {params.id} / videos</p>
        <h1 className="text-2xl font-semibold text-gray-900">動画一覧</h1>
        <p className="text-sm text-gray-500">
          バックエンドの `getChannelVideos` API を使用して動画一覧を表示します。ソートやフィルター機能も利用できます。
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
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="mt-2 w-full rounded-xl border border-gray-200 px-4 py-2 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
            >
              <option value="views_desc">再生数（降順）</option>
              <option value="views_asc">再生数（昇順）</option>
              <option value="published_desc">投稿日（新しい順）</option>
              <option value="published_asc">投稿日（古い順）</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-gray-500">期間フィルター</label>
            <div className="mt-2 flex gap-3">
              <input
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                className="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              />
              <input
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                className="w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              />
            </div>
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-gray-500">最低再生数</label>
            <input
              type="number"
              value={minViews}
              onChange={(e) => setMinViews(e.target.value)}
              placeholder="例: 1000"
              className="mt-2 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
            />
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-gray-100 bg-white shadow-sm">
        {isLoading ? (
          <div className="p-6 text-center">
            <p className="text-sm text-gray-500">読み込み中...</p>
          </div>
        ) : error ? (
          <div className="p-6 text-center">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : videos.length === 0 ? (
          <div className="p-6 text-center">
            <p className="text-sm text-gray-500">動画がありません</p>
          </div>
        ) : (
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
        )}
      </section>
    </div>
  );
}

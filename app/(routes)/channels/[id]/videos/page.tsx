"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { getChannelVideos } from "@/lib/api";
import type { Video, VideoListResponse } from "@/types/video";

type SortOption =
  | "published_desc"
  | "published_asc"
  | "views_desc"
  | "views_asc"
  | "likes_desc"
  | "likes_asc"
  | "comments_desc"
  | "comments_asc";

const ITEMS_PER_PAGE = 20;

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  }
  return `${minutes}:${secs.toString().padStart(2, "0")}`;
}

export default function ChannelVideosPage() {
  const params = useParams();
  const channelId = parseInt(params.id as string, 10);

  const [videos, setVideos] = useState<Video[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [sort, setSort] = useState<SortOption>("published_desc");
  const [currentPage, setCurrentPage] = useState(1);
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
        const params: Parameters<typeof getChannelVideos>[1] = {
          sort,
          limit: ITEMS_PER_PAGE,
          offset: (currentPage - 1) * ITEMS_PER_PAGE,
        };
        if (fromDate) params.from = fromDate;
        if (toDate) params.to = toDate;
        if (minViews) params.minViews = parseInt(minViews, 10);

        const data: VideoListResponse = await getChannelVideos(
          channelId,
          params
        );
        setVideos(data.items);
        setTotalCount(data.totalCount);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "動画一覧の取得に失敗しました"
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchVideos();
  }, [channelId, sort, currentPage, fromDate, toDate, minViews]);

  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">動画一覧</h1>
        <p className="mt-2 text-sm text-gray-500">
          合計 {totalCount} 本の動画
        </p>
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label
                htmlFor="sort"
                className="block text-xs font-medium text-gray-700"
              >
                ソート
              </label>
              <select
                id="sort"
                value={sort}
                onChange={(e) => {
                  setSort(e.target.value as SortOption);
                  setCurrentPage(1);
                }}
                className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              >
                <option value="published_desc">投稿日時（新しい順）</option>
                <option value="published_asc">投稿日時（古い順）</option>
                <option value="views_desc">再生数（多い順）</option>
                <option value="views_asc">再生数（少ない順）</option>
                <option value="likes_desc">高評価数（多い順）</option>
                <option value="likes_asc">高評価数（少ない順）</option>
                <option value="comments_desc">コメント数（多い順）</option>
                <option value="comments_asc">コメント数（少ない順）</option>
              </select>
            </div>
            <div>
              <label
                htmlFor="fromDate"
                className="block text-xs font-medium text-gray-700"
              >
                開始日
              </label>
              <input
                id="fromDate"
                type="date"
                value={fromDate}
                onChange={(e) => {
                  setFromDate(e.target.value);
                  setCurrentPage(1);
                }}
                className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              />
            </div>
            <div>
              <label
                htmlFor="toDate"
                className="block text-xs font-medium text-gray-700"
              >
                終了日
              </label>
              <input
                id="toDate"
                type="date"
                value={toDate}
                onChange={(e) => {
                  setToDate(e.target.value);
                  setCurrentPage(1);
                }}
                className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              />
            </div>
            <div>
              <label
                htmlFor="minViews"
                className="block text-xs font-medium text-gray-700"
              >
                最低再生数
              </label>
              <input
                id="minViews"
                type="number"
                value={minViews}
                onChange={(e) => {
                  setMinViews(e.target.value);
                  setCurrentPage(1);
                }}
                placeholder="例: 10000"
                className="mt-1 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              />
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-sm text-gray-500">読み込み中...</p>
        </div>
      ) : videos.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-sm text-gray-500">動画が見つかりませんでした</p>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {videos.map((video) => (
              <Link
                key={video.id}
                href={`https://www.youtube.com/watch?v=${video.youtubeVideoId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="group rounded-2xl border border-gray-100 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
              >
                <div className="relative aspect-video w-full overflow-hidden rounded-t-2xl">
                  <Image
                    src={video.thumbnailUrl}
                    alt={video.title}
                    fill
                    className="object-cover transition group-hover:scale-105"
                    unoptimized
                  />
                </div>
                <div className="p-4">
                  <h3 className="line-clamp-2 text-sm font-semibold text-gray-900 group-hover:text-youtube-red">
                    {video.title}
                  </h3>
                  <div className="mt-3 space-y-1 text-xs text-gray-500">
                    <p>
                      投稿日:{" "}
                      {new Date(video.publishedAt).toLocaleDateString("ja-JP")}
                    </p>
                    <p>再生数: {video.latestStats.viewCount.toLocaleString()}</p>
                    <p>
                      高評価: {video.latestStats.likeCount.toLocaleString()}
                    </p>
                    <p>
                      コメント:{" "}
                      {video.latestStats.commentCount.toLocaleString()}
                    </p>
                    <p>長さ: {formatDuration(video.durationSec)}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
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
  );
}


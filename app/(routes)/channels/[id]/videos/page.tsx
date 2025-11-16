"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

import { getChannelVideos } from "@/lib/api";
import { formatVideoListItem } from "@/utils/format";
import type { PageProps } from "@/types/page";
import type { VideoListItem } from "@/types/video";

export default function ChannelVideosPage({ params }: PageProps) {
  const [channelId, setChannelId] = useState<number | null>(null);
  const [channelIdString, setChannelIdString] = useState<string>("");
  const [videos, setVideos] = useState<VideoListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sort, setSort] = useState("views_desc");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [minViews, setMinViews] = useState("");

  // paramsがPromiseの場合は解決してからchannelIdを設定
  useEffect(() => {
    const resolveParams = async () => {
      const resolvedParams = params instanceof Promise ? await params : params;
      const id = parseInt(resolvedParams.id, 10);
      setChannelId(id);
      setChannelIdString(resolvedParams.id);
    };
    resolveParams();
  }, [params]);

  useEffect(() => {
    if (channelId === null) {
      return;
    }

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
        <p className="text-sm uppercase tracking-wide text-gray-500">channels / {channelIdString} / videos</p>
        <h1 className="text-2xl font-semibold text-gray-900">動画一覧</h1>
        <p className="text-sm text-gray-500">
          バックエンドの `getChannelVideos` API を使用して動画一覧を表示します。ソートやフィルター機能も利用できます。
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/channels/${channelIdString}`}
            className="btn-glass"
          >
            チャンネル詳細に戻る
          </Link>
          <Link
            href="/channels"
            className="btn-glass"
          >
            一覧へ戻る
          </Link>
        </div>
      </header>

      <section className="modern-card">
        <div className="card-inner">
          <div className="grid gap-8 grid-cols-1 md:grid-cols-2">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-gray-500">並び替え</label>
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value)}
                className="mt-2 w-full rounded-2xl border border-gray-200 px-4 py-3 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
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
                  className="w-full rounded-2xl border border-gray-200 px-3 py-3 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
                />
                <input
                  type="date"
                  value={toDate}
                  onChange={(e) => setToDate(e.target.value)}
                  className="w-full rounded-2xl border border-gray-200 px-3 py-3 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
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
                className="mt-2 w-full rounded-2xl border border-gray-200 px-3 py-3 text-sm text-gray-700 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
              />
            </div>
          </div>
        </div>
      </section>

      <section className="modern-card">
        <div className="card-inner">
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
          <div className="grid gap-8 grid-cols-1 md:grid-cols-2">
            {videos.map((video) => (
              <div key={video.id} className="channel-card">
                <div className="channel-inner">
                  <p className="channel-title">{video.title}</p>
                  <p className="text-xs text-gray-500 mb-2">ID: {video.id}</p>
                  <div className="channel-stats">
                    <div className="channel-stat">
                      <span className="icon">
                        <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M0 0h24v24H0z" fill="none"></path>
                          <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                        </svg>
                      </span>
                      <span>公開日: <strong>{video.publishedAt}</strong></span>
                    </div>
                    <div className="channel-stat">
                      <span className="icon">
                        <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M0 0h24v24H0z" fill="none"></path>
                          <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                        </svg>
                      </span>
                      <span>再生数: <strong>{video.views}</strong></span>
                    </div>
                    <div className="channel-stat">
                      <span className="icon">
                        <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M0 0h24v24H0z" fill="none"></path>
                          <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                        </svg>
                      </span>
                      <span>高評価: <strong>{video.likes}</strong></span>
                    </div>
                    <div className="channel-stat">
                      <span className="icon">
                        <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M0 0h24v24H0z" fill="none"></path>
                          <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                        </svg>
                      </span>
                      <span>コメント: <strong>{video.comments}</strong></span>
                    </div>
                    <div className="channel-stat">
                      <span className="icon">
                        <svg height="24" width="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M0 0h24v24H0z" fill="none"></path>
                          <path fill="currentColor" d="M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z"></path>
                        </svg>
                      </span>
                      <span>尺: <strong>{video.duration}</strong></span>
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

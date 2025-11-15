"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { importChannel } from "@/lib/api";
import type { ChannelImportResponse } from "@/types/channel";

export default function ChannelImportPage() {
  const router = useRouter();
  const [channelUrlOrId, setChannelUrlOrId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    if (!channelUrlOrId.trim()) {
      setError("チャンネルURLまたはIDを入力してください");
      return;
    }

    setIsLoading(true);
    try {
      const result: ChannelImportResponse = await importChannel(
        channelUrlOrId.trim()
      );
      router.push(`/channels/${result.channel.id}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "チャンネルのインポートに失敗しました"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          チャンネルを登録
        </h1>
        <p className="mt-2 text-sm text-gray-500">
          YouTubeチャンネルURLまたはチャンネルIDを入力してください
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="channelUrlOrId"
            className="block text-sm font-medium text-gray-700"
          >
            チャンネルURLまたはID
          </label>
          <input
            id="channelUrlOrId"
            type="text"
            value={channelUrlOrId}
            onChange={(e) => setChannelUrlOrId(e.target.value)}
            placeholder="https://www.youtube.com/@hoge または UCxxxxxx"
            className="mt-2 w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
            disabled={isLoading}
          />
          {error && (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="rounded-xl bg-youtube-red px-6 py-3 text-sm font-semibold text-white transition hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? "登録中..." : "チャンネルを登録"}
        </button>
      </form>
    </div>
  );
}


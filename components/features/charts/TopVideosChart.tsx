"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { Video } from "@/types/video";

interface TopVideosChartProps {
  videos: Video[];
}

export default function TopVideosChart({ videos }: TopVideosChartProps) {
  const topVideos = videos
    .sort((a, b) => b.latestStats.viewCount - a.latestStats.viewCount)
    .slice(0, 10)
    .map((video) => ({
      title: video.title.length > 30 ? `${video.title.substring(0, 30)}...` : video.title,
      views: video.latestStats.viewCount,
    }));

  if (topVideos.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-gray-500">
        データがありません
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={topVideos} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="title"
          angle={-45}
          textAnchor="end"
          height={100}
          interval={0}
          tick={{ fontSize: 12 }}
        />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip
          formatter={(value: number) => [`${value.toLocaleString()}回`, "再生数"]}
          labelStyle={{ color: "#374151" }}
        />
        <Bar dataKey="views" fill="#ef4444" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}



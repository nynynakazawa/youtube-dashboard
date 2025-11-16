"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { Video } from "@/types/video";

interface MonthlyViewsChartProps {
  videos: Video[];
}

export default function MonthlyViewsChart({ videos }: MonthlyViewsChartProps) {
  const monthlyData = videos.reduce((acc, video) => {
    const date = new Date(video.publishedAt);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
    const monthLabel = `${date.getFullYear()}年${date.getMonth() + 1}月`;

    if (!acc[monthKey]) {
      acc[monthKey] = { month: monthLabel, views: 0 };
    }
    acc[monthKey].views += video.latestStats.viewCount;
    return acc;
  }, {} as Record<string, { month: string; views: number }>);

  const chartData = Object.entries(monthlyData)
    .sort(([aKey], [bKey]) => aKey.localeCompare(bKey))
    .map(([, value]) => value);

  if (chartData.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-gray-500">
        データがありません
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip
          formatter={(value: number) => [`${value.toLocaleString()}回`, "再生数"]}
          labelStyle={{ color: "#374151" }}
        />
        <Line type="monotone" dataKey="views" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}


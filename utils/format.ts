import type {
  ChannelListItem as FrontendChannelListItem,
  BackendChannelListItem,
} from "@/types/channel";
import type {
  VideoListItem as FrontendVideoListItem,
  BackendVideoListItem,
} from "@/types/video";

export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return "0";
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");
  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");
  return `${month}/${day} ${hours}:${minutes}`;
}

function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined) return "-";
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }
  return `${minutes}:${secs.toString().padStart(2, "0")}`;
}

export function formatChannelListItem(
  channel: BackendChannelListItem
): FrontendChannelListItem {
  return {
    id: channel.id.toString(),
    name: channel.title,
    subscribers: formatNumber(channel.subscriberCount),
    totalViews: formatNumber(channel.viewCount),
    videos: channel.videoCount ?? 0,
    lastFetched: "-",
  };
}

export function formatVideoListItem(
  video: BackendVideoListItem
): FrontendVideoListItem {
  return {
    id: video.id.toString(),
    title: video.title,
    publishedAt: new Date(video.publishedAt).toLocaleDateString("ja-JP"),
    views: formatNumber(video.latestStats.viewCount),
    likes: formatNumber(video.latestStats.likeCount),
    comments: formatNumber(video.latestStats.commentCount),
    duration: formatDuration(video.durationSec),
  };
}


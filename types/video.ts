export interface VideoStats {
  viewCount: number;
  likeCount: number;
  commentCount: number;
}

export interface Video {
  id: number;
  youtubeVideoId: string;
  title: string;
  thumbnailUrl: string;
  publishedAt: string;
  durationSec: number;
  latestStats: VideoStats;
}

export interface VideoListResponse {
  items: Video[];
  totalCount: number;
}


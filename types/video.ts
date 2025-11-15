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

export interface BackendVideoListItem {
  id: number;
  youtubeVideoId: string;
  title: string;
  thumbnailUrl: string | null;
  publishedAt: string;
  durationSec: number | null;
  latestStats: {
    viewCount: number;
    likeCount: number | null;
    commentCount: number | null;
  };
}

export interface VideoListItem {
  id: string;
  title: string;
  publishedAt: string;
  views: string;
  likes: string;
  comments: string;
  duration: string;
}

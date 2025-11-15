export interface Channel {
  id: number;
  youtubeChannelId: string;
  title: string;
  description: string;
  publishedAt: string;
  subscriberCount: number;
  videoCount: number;
  viewCount: number;
}

export interface ChannelSummary {
  totalViews: number;
  totalVideos: number;
  lastFetchedAt: string;
}

export interface ChannelImportResponse {
  channel: Channel;
  summary: ChannelSummary;
}

export interface ChannelListItem {
  id: string;
  name: string;
  subscribers: string;
  totalViews: string;
  videos: number;
  lastFetched: string;
}

export interface BackendChannelListItem {
  id: number;
  youtubeChannelId: string;
  title: string;
  subscriberCount: number | null;
  viewCount: number | null;
  videoCount: number | null;
}

export interface ChannelListResponse {
  items: BackendChannelListItem[];
  totalCount: number;
}

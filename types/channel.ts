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


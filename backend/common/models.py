from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ChannelResponse(BaseModel):
    id: int
    youtubeChannelId: str
    title: str
    description: Optional[str]
    publishedAt: Optional[datetime]
    subscriberCount: Optional[int]
    videoCount: Optional[int]
    viewCount: Optional[int]


class SummaryResponse(BaseModel):
    totalViews: int
    totalVideos: int
    lastFetchedAt: datetime


class ChannelImportResponse(BaseModel):
    channel: ChannelResponse
    summary: SummaryResponse


class ChannelListItem(BaseModel):
    id: int
    youtubeChannelId: str
    title: str
    subscriberCount: Optional[int]
    viewCount: Optional[int]
    videoCount: Optional[int]


class ChannelListResponse(BaseModel):
    items: list[ChannelListItem]
    totalCount: int


class VideoStats(BaseModel):
    viewCount: int
    likeCount: Optional[int]
    commentCount: Optional[int]


class VideoListItem(BaseModel):
    id: int
    youtubeVideoId: str
    title: str
    thumbnailUrl: Optional[str]
    publishedAt: datetime
    durationSec: Optional[int]
    latestStats: VideoStats


class VideoListResponse(BaseModel):
    items: list[VideoListItem]
    totalCount: int



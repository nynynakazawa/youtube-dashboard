import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from common.logger import get_logger
from constants.config import YOUTUBE_API_KEY

logger = get_logger(__name__)
BASE_URL = "https://www.googleapis.com/youtube/v3"


class YouTubeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        logger.debug("YouTubeClient initialized")

    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        logger.info("Fetching channel info from YouTube API", extra={"channel_id": channel_id})
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": channel_id,
            "key": self.api_key,
        }
        response = requests.get(f"{BASE_URL}/channels", params=params)
        logger.debug("YouTube API response", extra={"status_code": response.status_code})
        response.raise_for_status()
        data = response.json()

        if not data.get("items"):
            logger.warning("Channel not found in YouTube API", extra={"channel_id": channel_id})
            raise ValueError("Channel not found")

        item = data["items"][0]
        snippet = item["snippet"]
        statistics = item["statistics"]
        content_details = item.get("contentDetails", {})

        channel_info = {
            "channel_id": channel_id,
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "published_at": snippet["publishedAt"],
            "subscriber_count": int(statistics.get("subscriberCount", 0)),
            "video_count": int(statistics.get("videoCount", 0)),
            "view_count": int(statistics.get("viewCount", 0)),
            "upload_playlist_id": content_details.get("relatedPlaylists", {}).get("uploads"),
        }
        logger.info("Channel info fetched successfully", extra={"channel_id": channel_id, "title": channel_info["title"], "video_count": channel_info["video_count"]})
        return channel_info

    def get_all_video_ids(self, upload_playlist_id: str) -> List[str]:
        logger.info("Fetching all video IDs from playlist", extra={"upload_playlist_id": upload_playlist_id})
        video_ids = []
        next_page_token = None
        page_count = 0

        while True:
            page_count += 1
            params = {
                "part": "contentDetails",
                "playlistId": upload_playlist_id,
                "maxResults": 50,
                "key": self.api_key,
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            logger.debug("Fetching playlist items page", extra={"page": page_count, "playlist_id": upload_playlist_id})
            response = requests.get(f"{BASE_URL}/playlistItems", params=params)
            logger.debug("Playlist items API response", extra={"status_code": response.status_code})
            response.raise_for_status()
            data = response.json()

            page_video_ids = [
                item["contentDetails"]["videoId"]
                for item in data.get("items", [])
            ]
            video_ids.extend(page_video_ids)
            logger.debug("Video IDs fetched from page", extra={"page": page_count, "count": len(page_video_ids), "total": len(video_ids)})

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        logger.info("All video IDs fetched successfully", extra={"total_videos": len(video_ids), "pages": page_count})
        return video_ids

    def _fetch_video_chunk(self, chunk: List[str], chunk_idx: int, total_chunks: int) -> List[Dict[str, Any]]:
        logger.debug("Fetching video info chunk", extra={"chunk": chunk_idx, "total_chunks": total_chunks, "chunk_size": len(chunk)})
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(chunk),
            "key": self.api_key,
        }

        response = requests.get(f"{BASE_URL}/videos", params=params)
        logger.debug("Videos API response", extra={"status_code": response.status_code, "chunk": chunk_idx})
        response.raise_for_status()
        data = response.json()

        videos = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            statistics = item["statistics"]
            content_details = item.get("contentDetails", {})

            duration_str = content_details.get("duration", "")
            duration_sec = self._parse_duration(duration_str)

            video_info = {
                "video_id": item["id"],
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "published_at": snippet["publishedAt"],
                "duration_sec": duration_sec,
                "tags": snippet.get("tags", []),
                "thumbnail_url": snippet.get("thumbnails", {})
                .get("default", {})
                .get("url"),
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
            }
            videos.append(video_info)

        logger.debug("Video info chunk processed", extra={"chunk": chunk_idx, "processed": len(videos)})
        return videos

    def get_videos_info(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        logger.info("Fetching videos info from YouTube API", extra={"total_videos": len(video_ids)})
        if not video_ids:
            return []

        chunk_size = 50
        chunks = [
            video_ids[i : i + chunk_size]
            for i in range(0, len(video_ids), chunk_size)
        ]
        total_chunks = len(chunks)

        all_videos = []
        max_workers = min(10, total_chunks)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_chunk = {
                executor.submit(self._fetch_video_chunk, chunk, idx + 1, total_chunks): idx
                for idx, chunk in enumerate(chunks)
            }

            for future in as_completed(future_to_chunk):
                chunk_idx = future_to_chunk[future]
                try:
                    videos = future.result()
                    all_videos.extend(videos)
                except Exception as e:
                    logger.error(
                        "Error fetching video chunk",
                        extra={"chunk": chunk_idx + 1, "error": str(e), "error_type": type(e).__name__},
                        exc_info=True
                    )
                    raise

        logger.info("All videos info fetched successfully", extra={"total_videos": len(all_videos)})
        return all_videos

    def _parse_duration(self, duration_str: str) -> Optional[int]:
        if not duration_str:
            return None

        import re

        pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
        match = re.match(pattern, duration_str)

        if not match:
            return None

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds


def get_youtube_client() -> YouTubeClient:
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY is not set")
        raise ValueError("YOUTUBE_API_KEY is not set")
    logger.debug("Creating YouTubeClient instance")
    return YouTubeClient(YOUTUBE_API_KEY)


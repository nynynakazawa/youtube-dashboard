from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from common.logger import get_logger
from db.rds import get_db_connection
from services.youtube_client import YouTubeClient

logger = get_logger(__name__)


def upsert_channel(
    youtube_channel_id: str,
    title: str,
    description: str,
    published_at: Optional[datetime],
    subscriber_count: int,
    video_count: int,
    view_count: int,
) -> int:
    logger.info("Upserting channel", extra={"youtube_channel_id": youtube_channel_id, "title": title})
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO channels (
                    youtube_channel_id, title, description, published_at,
                    subscriber_count, video_count, view_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    description = VALUES(description),
                    published_at = VALUES(published_at),
                    subscriber_count = VALUES(subscriber_count),
                    video_count = VALUES(video_count),
                    view_count = VALUES(view_count),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    youtube_channel_id,
                    title,
                    description,
                    published_at,
                    subscriber_count,
                    video_count,
                    view_count,
                ),
            )
            channel_id = cursor.lastrowid
            if not channel_id:
                logger.debug("Channel already exists, fetching ID", extra={"youtube_channel_id": youtube_channel_id})
                cursor.execute(
                    "SELECT id FROM channels WHERE youtube_channel_id = %s",
                    (youtube_channel_id,),
                )
                result = cursor.fetchone()
                channel_id = result["id"]
            logger.info("Channel upserted successfully", extra={"channel_id": channel_id, "youtube_channel_id": youtube_channel_id})
            return channel_id


def upsert_videos(channel_id: int, videos: List[Dict[str, Any]]) -> None:
    logger.info("Upserting videos", extra={"channel_id": channel_id, "video_count": len(videos)})
    if not videos:
        logger.debug("No videos to upsert")
        return

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            video_values = []
            for video in videos:
                published_at = datetime.fromisoformat(
                    video["published_at"].replace("Z", "+00:00")
                )
                video_values.append((
                    channel_id,
                    video["video_id"],
                    video["title"],
                    video["description"],
                    published_at,
                    video["duration_sec"],
                    json.dumps(video["tags"]) if video["tags"] else None,
                ))

            cursor.executemany(
                """
                INSERT INTO videos (
                    channel_id, youtube_video_id, title, description,
                    published_at, duration_sec, tags_json
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    description = VALUES(description),
                    published_at = VALUES(published_at),
                    duration_sec = VALUES(duration_sec),
                    tags_json = VALUES(tags_json),
                    updated_at = CURRENT_TIMESTAMP
                """,
                video_values,
            )
            logger.debug("Videos batch inserted", extra={"count": len(video_values)})

            youtube_video_ids = [video["video_id"] for video in videos]
            placeholders = ",".join(["%s"] * len(youtube_video_ids))
            cursor.execute(
                f"""
                SELECT id, youtube_video_id
                FROM videos
                WHERE youtube_video_id IN ({placeholders})
                """,
                youtube_video_ids,
            )
            video_id_map = {row["youtube_video_id"]: row["id"] for row in cursor.fetchall()}

            stats_values = []
            for video in videos:
                video_db_id = video_id_map.get(video["video_id"])
                if video_db_id:
                    stats_values.append((
                        video_db_id,
                        video["view_count"],
                        video["like_count"],
                        video["comment_count"],
                    ))

            if stats_values:
                cursor.executemany(
                    """
                    INSERT INTO video_stats_history (
                        video_id, snapshot_at, view_count, like_count, comment_count
                    ) VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s)
                    """,
                    stats_values,
                )
                logger.debug("Video stats batch inserted", extra={"count": len(stats_values)})

    logger.info("Videos upserted successfully", extra={"channel_id": channel_id, "total_videos": len(videos)})


def get_channel_by_youtube_id(youtube_channel_id: str) -> Optional[Dict[str, Any]]:
    logger.debug("Getting channel by YouTube ID", extra={"youtube_channel_id": youtube_channel_id})
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, youtube_channel_id, title, description, published_at,
                       subscriber_count, video_count, view_count
                FROM channels
                WHERE youtube_channel_id = %s
                """,
                (youtube_channel_id,),
            )
            result = cursor.fetchone()
            if result:
                logger.debug("Channel found", extra={"channel_id": result["id"], "youtube_channel_id": youtube_channel_id})
            else:
                logger.debug("Channel not found", extra={"youtube_channel_id": youtube_channel_id})
            return result


def get_channel_by_id(channel_id: int) -> Optional[Dict[str, Any]]:
    logger.debug("Getting channel by ID", extra={"channel_id": channel_id})
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, youtube_channel_id, title, description, published_at,
                       subscriber_count, video_count, view_count
                FROM channels
                WHERE id = %s
                """,
                (channel_id,),
            )
            result = cursor.fetchone()
            if result:
                logger.debug("Channel found", extra={"channel_id": channel_id})
            else:
                logger.debug("Channel not found", extra={"channel_id": channel_id})
            return result


def import_channel_data(youtube_channel_id: str, youtube_client: YouTubeClient) -> Dict[str, Any]:
    logger.info("Starting channel data import", extra={"youtube_channel_id": youtube_channel_id})
    channel_info = youtube_client.get_channel_info(youtube_channel_id)

    if not channel_info.get("upload_playlist_id"):
        logger.error("Upload playlist not found", extra={"youtube_channel_id": youtube_channel_id})
        raise ValueError("Upload playlist not found")

    logger.info("Fetching video IDs from upload playlist", extra={"upload_playlist_id": channel_info["upload_playlist_id"]})
    video_ids = youtube_client.get_all_video_ids(channel_info["upload_playlist_id"])
    logger.info("Video IDs fetched", extra={"count": len(video_ids)})

    videos_info = youtube_client.get_videos_info(video_ids)

    published_at = None
    if channel_info["published_at"]:
        published_at = datetime.fromisoformat(
            channel_info["published_at"].replace("Z", "+00:00")
        )

    channel_db_id = upsert_channel(
        youtube_channel_id=channel_info["channel_id"],
        title=channel_info["title"],
        description=channel_info["description"],
        published_at=published_at,
        subscriber_count=channel_info["subscriber_count"],
        video_count=channel_info["video_count"],
        view_count=channel_info["view_count"],
    )

    upsert_videos(channel_db_id, videos_info)

    total_views = sum(video["view_count"] for video in videos_info)

    result = {
        "channel_id": channel_db_id,
        "total_views": total_views,
        "total_videos": len(videos_info),
    }
    logger.info("Channel data import completed", extra={"channel_id": channel_db_id, "total_videos": result["total_videos"], "total_views": result["total_views"]})
    return result


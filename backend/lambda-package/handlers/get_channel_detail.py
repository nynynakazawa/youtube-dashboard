from datetime import datetime
from typing import Dict, Any

from common.response import success_response, error_response
from common.logger import get_logger
from common.models import ChannelImportResponse, ChannelResponse, SummaryResponse
from services.channel_service import get_channel_by_id
from db.rds import get_db_connection

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("get_channel_detail handler started", extra={"event": event})
    try:
        path_params = event.get("pathParameters") or {}
        channel_id_str = path_params.get("id")

        logger.info("Request received", extra={"channel_id": channel_id_str})

        if not channel_id_str:
            logger.warning("Channel ID is missing")
            return error_response("INVALID_PARAMETER", "チャンネルIDは必須です", 400)

        try:
            channel_id = int(channel_id_str)
        except ValueError:
            logger.warning("Invalid channel ID format", extra={"channel_id": channel_id_str})
            return error_response("INVALID_PARAMETER", "チャンネルIDが不正です", 400)

        channel = get_channel_by_id(channel_id)
        if not channel:
            logger.warning("Channel not found", extra={"channel_id": channel_id})
            return error_response("NOT_FOUND", "指定されたチャンネルが見つかりませんでした", 404)

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        COUNT(DISTINCT v.id) as total_videos,
                        COALESCE(SUM(latest_stats.view_count), 0) as total_views
                    FROM videos v
                    LEFT JOIN (
                        SELECT 
                            video_id,
                            view_count,
                            ROW_NUMBER() OVER (PARTITION BY video_id ORDER BY snapshot_at DESC) as rn
                        FROM video_stats_history
                    ) latest_stats ON v.id = latest_stats.video_id AND latest_stats.rn = 1
                    WHERE v.channel_id = %s
                    """,
                    (channel_id,),
                )
                stats_result = cursor.fetchone()

                total_videos = stats_result["total_videos"] if stats_result else 0
                total_views = stats_result["total_views"] if stats_result else 0

        logger.debug("Channel stats fetched", extra={"channel_id": channel_id, "total_videos": total_videos, "total_views": total_views})

        response = ChannelImportResponse(
            channel=ChannelResponse(
                id=channel["id"],
                youtubeChannelId=channel["youtube_channel_id"],
                title=channel["title"],
                description=channel["description"],
                publishedAt=channel["published_at"],
                subscriberCount=channel["subscriber_count"],
                videoCount=channel["video_count"],
                viewCount=channel["view_count"],
            ),
            summary=SummaryResponse(
                totalViews=total_views or 0,
                totalVideos=total_videos or 0,
                lastFetchedAt=datetime.now(),
            ),
        )

        logger.info("get_channel_detail handler completed successfully", extra={"channel_id": channel_id})
        return success_response(response.model_dump(mode="json"))

    except Exception as e:
        logger.error("Unexpected error occurred", extra={"error": str(e), "error_type": type(e).__name__}, exc_info=True)
        return error_response("INTERNAL_ERROR", "サーバーエラーが発生しました。しばらく待ってから再度お試しください", 500)


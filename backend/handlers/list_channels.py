from typing import Dict, Any

from common.response import success_response, error_response
from common.logger import get_logger
from common.models import ChannelListResponse, ChannelListItem
from db.rds import get_db_connection

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("list_channels handler started", extra={"event": event})
    try:
        query_params = event.get("queryStringParameters") or {}
        q = query_params.get("q", "")
        limit = int(query_params.get("limit", "20"))
        offset = int(query_params.get("offset", "0"))

        logger.info("Query parameters", extra={"q": q, "limit": limit, "offset": offset})

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                if q:
                    cursor.execute(
                        """
                        SELECT COUNT(*) as total
                        FROM channels
                        WHERE title LIKE %s
                        """,
                        (f"%{q}%",),
                    )
                    total_result = cursor.fetchone()
                    total_count = total_result["total"] if total_result else 0

                    cursor.execute(
                        """
                        SELECT id, youtube_channel_id, title, subscriber_count,
                               view_count, video_count
                        FROM channels
                        WHERE title LIKE %s
                        ORDER BY id DESC
                        LIMIT %s OFFSET %s
                        """,
                        (f"%{q}%", limit, offset),
                    )
                else:
                    cursor.execute("SELECT COUNT(*) as total FROM channels")
                    total_result = cursor.fetchone()
                    total_count = total_result["total"] if total_result else 0

                    cursor.execute(
                        """
                        SELECT id, youtube_channel_id, title, subscriber_count,
                               view_count, video_count
                        FROM channels
                        ORDER BY id DESC
                        LIMIT %s OFFSET %s
                        """,
                        (limit, offset),
                    )

                rows = cursor.fetchall()

        logger.debug("Channels fetched", extra={"count": len(rows), "total_count": total_count})

        items = [
            ChannelListItem(
                id=row["id"],
                youtubeChannelId=row["youtube_channel_id"],
                title=row["title"],
                subscriberCount=row["subscriber_count"],
                viewCount=row["view_count"],
                videoCount=row["video_count"],
            )
            for row in rows
        ]

        response = ChannelListResponse(items=items, totalCount=total_count)
        logger.info("list_channels handler completed successfully", extra={"item_count": len(items), "total_count": total_count})
        return success_response(response.model_dump(mode="json"))

    except Exception as e:
        logger.error("Unexpected error occurred", extra={"error": str(e), "error_type": type(e).__name__}, exc_info=True)
        return error_response("INTERNAL_ERROR", "サーバーエラーが発生しました。しばらく待ってから再度お試しください", 500)


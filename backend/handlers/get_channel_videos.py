from datetime import datetime
from typing import Dict, Any, Optional

from common.response import success_response, error_response
from common.logger import get_logger
from common.models import VideoListResponse, VideoListItem, VideoStats
from services.channel_service import get_channel_by_id
from db.rds import get_db_connection

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("get_channel_videos handler started", extra={"event": event})
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

        query_params = event.get("queryStringParameters") or {}
        sort = query_params.get("sort", "date_desc")
        limit = int(query_params.get("limit", "20"))
        offset = int(query_params.get("offset", "0"))
        from_date = query_params.get("from")
        to_date = query_params.get("to")
        min_views = query_params.get("minViews")

        logger.info("Query parameters", extra={"sort": sort, "limit": limit, "offset": offset, "from_date": from_date, "to_date": to_date, "min_views": min_views})

        order_by_map = {
            "views_desc": "COALESCE(latest_stats.view_count, 0) DESC",
            "views_asc": "COALESCE(latest_stats.view_count, 0) ASC",
            "likes_desc": "COALESCE(latest_stats.like_count, 0) DESC",
            "comments_desc": "COALESCE(latest_stats.comment_count, 0) DESC",
            "date_desc": "v.published_at DESC",
            "date_asc": "v.published_at ASC",
        }
        order_by = order_by_map.get(sort, "v.published_at DESC")

        conditions = ["v.channel_id = %s"]
        params = [channel_id]

        if from_date:
            conditions.append("DATE(v.published_at) >= %s")
            params.append(from_date)

        if to_date:
            conditions.append("DATE(v.published_at) <= %s")
            params.append(to_date)

        where_clause = " AND ".join(conditions)

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                base_query = f"""
                    FROM videos v
                    LEFT JOIN (
                        SELECT 
                            video_id,
                            view_count,
                            like_count,
                            comment_count,
                            ROW_NUMBER() OVER (PARTITION BY video_id ORDER BY snapshot_at DESC) as rn
                        FROM video_stats_history
                    ) latest_stats ON v.id = latest_stats.video_id AND latest_stats.rn = 1
                    WHERE {where_clause}
                """

                if min_views:
                    base_query = base_query.replace(
                        "WHERE " + where_clause,
                        f"WHERE {where_clause} AND COALESCE(latest_stats.view_count, 0) >= %s"
                    )
                    params.append(int(min_views))

                cursor.execute(
                    f"SELECT COUNT(*) as total {base_query}",
                    tuple(params),
                )
                total_result = cursor.fetchone()
                total_count = total_result["total"] if total_result else 0

                params.extend([limit, offset])
                cursor.execute(
                    f"""
                    SELECT 
                        v.id, 
                        v.youtube_video_id, 
                        v.title, 
                        v.published_at,
                        v.duration_sec, 
                        COALESCE(latest_stats.view_count, 0) as view_count,
                        COALESCE(latest_stats.like_count, 0) as like_count,
                        COALESCE(latest_stats.comment_count, 0) as comment_count
                    {base_query}
                    ORDER BY {order_by}
                    LIMIT %s OFFSET %s
                    """,
                    tuple(params),
                )
                rows = cursor.fetchall()

        logger.debug("Videos fetched", extra={"count": len(rows), "total_count": total_count})

        items = [
            VideoListItem(
                id=row["id"],
                youtubeVideoId=row["youtube_video_id"],
                title=row["title"],
                thumbnailUrl=f"https://i.ytimg.com/vi/{row['youtube_video_id']}/hqdefault.jpg",
                publishedAt=row["published_at"],
                durationSec=row["duration_sec"],
                latestStats=VideoStats(
                    viewCount=row["view_count"],
                    likeCount=row["like_count"],
                    commentCount=row["comment_count"],
                ),
            )
            for row in rows
        ]

        response = VideoListResponse(items=items, totalCount=total_count)
        logger.info("get_channel_videos handler completed successfully", extra={"channel_id": channel_id, "item_count": len(items), "total_count": total_count})
        return success_response(response.model_dump(mode="json"))

    except Exception as e:
        logger.error("Unexpected error occurred", extra={"error": str(e), "error_type": type(e).__name__}, exc_info=True)
        return error_response("INTERNAL_ERROR", "サーバーエラーが発生しました。しばらく待ってから再度お試しください", 500)


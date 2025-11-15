import json
from datetime import datetime
from typing import Dict, Any

from common.response import success_response, error_response
from common.logger import get_logger
from utils.extract_channel_id import extract_channel_id
from common.models import ChannelImportResponse, ChannelResponse, SummaryResponse
from db.dynamodb_cache import should_fetch, update_cache
from services.youtube_client import get_youtube_client
from services.channel_service import import_channel_data, get_channel_by_youtube_id

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("channel_import handler started", extra={"event": event})
    
    try:
        body = json.loads(event.get("body", "{}"))
        channel_url_or_id = body.get("channelUrlOrId")

        logger.info("Request received", extra={"channelUrlOrId": channel_url_or_id})

        if not channel_url_or_id:
            logger.warning("channelUrlOrId is missing")
            return error_response("INVALID_PARAMETER", "channelUrlOrIdは必須です", 400)

        youtube_channel_id = extract_channel_id(channel_url_or_id)
        logger.debug("Channel ID extracted", extra={"youtube_channel_id": youtube_channel_id})
        
        if not youtube_channel_id:
            logger.warning("Failed to extract channel ID", extra={"input": channel_url_or_id})
            return error_response("INVALID_PARAMETER", "チャンネルID抽出に失敗しました", 400)

        if not should_fetch(youtube_channel_id):
            logger.info("Rate limit check: using cached data", extra={"youtube_channel_id": youtube_channel_id})
            existing_channel = get_channel_by_youtube_id(youtube_channel_id)
            if not existing_channel:
                logger.warning("Channel not found in database", extra={"youtube_channel_id": youtube_channel_id})
                return error_response("NOT_FOUND", "指定されたチャンネルが見つかりませんでした", 404)

            logger.info("Returning cached channel data", extra={"channel_id": existing_channel["id"]})
            return success_response(
                ChannelImportResponse(
                    channel=ChannelResponse(
                        id=existing_channel["id"],
                        youtubeChannelId=existing_channel["youtube_channel_id"],
                        title=existing_channel["title"],
                        description=existing_channel["description"],
                        publishedAt=existing_channel["published_at"],
                        subscriberCount=existing_channel["subscriber_count"],
                        videoCount=existing_channel["video_count"],
                        viewCount=existing_channel["view_count"],
                    ),
                    summary=SummaryResponse(
                        totalViews=existing_channel["view_count"],
                        totalVideos=existing_channel["video_count"],
                        lastFetchedAt=datetime.now(),
                    ),
                ).model_dump(mode="json")
            )

        logger.info("Fetching channel data from YouTube API", extra={"youtube_channel_id": youtube_channel_id})
        youtube_client = get_youtube_client()
        import_result = import_channel_data(youtube_channel_id, youtube_client)
        logger.info("Channel data imported successfully", extra={"channel_id": import_result["channel_id"], "total_videos": import_result["total_videos"]})
        
        update_cache(youtube_channel_id)
        logger.debug("Cache updated", extra={"youtube_channel_id": youtube_channel_id})

        channel = get_channel_by_youtube_id(youtube_channel_id)
        if not channel:
            logger.error("Failed to retrieve channel after import", extra={"youtube_channel_id": youtube_channel_id})
            return error_response("INTERNAL_ERROR", "チャンネル情報の取得に失敗しました", 500)

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
                totalViews=import_result["total_views"],
                totalVideos=import_result["total_videos"],
                lastFetchedAt=datetime.now(),
            ),
        )

        logger.info("channel_import handler completed successfully", extra={"channel_id": channel["id"]})
        return success_response(response.model_dump(mode="json"))

    except json.JSONDecodeError as e:
        logger.error("JSON decode error", extra={"error": str(e), "body": event.get("body")})
        return error_response("INVALID_REQUEST", "リクエストボディのJSON形式が不正です", 400)
    except ValueError as e:
        error_message = str(e)
        logger.warning("ValueError occurred", extra={"error": error_message})
        if "not found" in error_message.lower():
            return error_response("NOT_FOUND", "指定されたチャンネルが見つかりませんでした", 404)
        return error_response("INVALID_PARAMETER", error_message, 400)
    except Exception as e:
        logger.error("Unexpected error occurred", extra={"error": str(e), "error_type": type(e).__name__}, exc_info=True)
        return error_response("INTERNAL_ERROR", "サーバーエラーが発生しました。しばらく待ってから再度お試しください", 500)


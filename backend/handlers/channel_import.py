import json
from datetime import datetime
from typing import Dict, Any

from common.response import success_response, error_response
from common.logger import get_logger
from utils.extract_channel_id import extract_channel_id, extract_handle
from common.models import ChannelImportResponse, ChannelResponse, SummaryResponse
from db.dynamodb_cache import should_fetch, update_cache
from services.youtube_client import get_youtube_client
from services.channel_service import import_channel_data, get_channel_by_youtube_id

logger = get_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    logger.info("channel_import handler started", extra={"event": event})
    
    try:
        # PayloadFormatVersion 2.0の場合、bodyは文字列として渡される
        # isBase64EncodedフラグでBase64エンコードされているかどうかを判定
        body_str = event.get("body", "{}")
        is_base64_encoded = event.get("isBase64Encoded", False)
        
        logger.info(f"Request body info: body_type={type(body_str).__name__}, is_base64_encoded={is_base64_encoded}, body_preview={str(body_str)[:200] if body_str else 'empty'}")
        
        # Base64エンコードされている場合はデコード
        if is_base64_encoded and isinstance(body_str, str) and body_str:
            try:
                import base64
                decoded_body = base64.b64decode(body_str).decode('utf-8')
                body = json.loads(decoded_body)
                logger.debug("Body was Base64 encoded", extra={"decoded": decoded_body[:200]})
            except Exception as e:
                logger.error("Failed to decode Base64 body", extra={"error": str(e), "body": body_str[:100]})
                return error_response("INVALID_REQUEST", "リクエストボディの形式が不正です", 400)
        elif isinstance(body_str, str) and body_str:
            # 通常のJSONパース
            try:
                body = json.loads(body_str)
            except json.JSONDecodeError as e:
                logger.error("JSON decode error", extra={"error": str(e), "body": body_str[:200]})
                return error_response("INVALID_REQUEST", "リクエストボディのJSON形式が不正です", 400)
        else:
            body = {}
        
        channel_url_or_id = body.get("channelUrlOrId")
        logger.info(f"Request received: channelUrlOrId={channel_url_or_id}, body_keys={list(body.keys())}, body={body}")

        if not channel_url_or_id:
            logger.warning("channelUrlOrId is missing")
            return error_response("INVALID_PARAMETER", "channelUrlOrIdは必須です", 400)

        logger.info(f"Extracting channel ID from: {channel_url_or_id}")
        youtube_channel_id = extract_channel_id(channel_url_or_id)
        logger.info(f"Channel ID extracted: {youtube_channel_id}")
        
        # チャンネルIDが抽出できなかった場合、ハンドル名を試す
        youtube_client = None
        if not youtube_channel_id:
            handle = extract_handle(channel_url_or_id)
            if handle:
                logger.info(f"Handle extracted: {handle}, fetching channel ID from YouTube API")
                try:
                    youtube_client = get_youtube_client()
                    youtube_channel_id = youtube_client.get_channel_id_from_handle(handle)
                    logger.info(f"Channel ID fetched from handle: {youtube_channel_id}")
                except Exception as e:
                    logger.error(f"Failed to get channel ID from handle: {str(e)}", exc_info=True)
                    return error_response("INVALID_PARAMETER", f"ハンドル名からチャンネルIDを取得できませんでした: {str(e)}", 400)
            else:
                logger.warning(f"Failed to extract channel ID or handle from input: {channel_url_or_id}")
                return error_response("INVALID_PARAMETER", "チャンネルIDまたはハンドル名の抽出に失敗しました", 400)

        logger.info(f"Checking if should fetch for channel ID: {youtube_channel_id}")
        should_fetch_result = should_fetch(youtube_channel_id)
        logger.info(f"should_fetch result: {should_fetch_result}")
        
        if not should_fetch_result:
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
        if not youtube_client:
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


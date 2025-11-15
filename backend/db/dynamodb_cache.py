import boto3
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from common.logger import get_logger
from constants.config import DYNAMODB_TABLE_NAME, MIN_FETCH_INTERVAL

logger = get_logger(__name__)
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def get_last_fetched_at(youtube_channel_id: str) -> Optional[int]:
    try:
        logger.debug("Getting last fetched time from DynamoDB", extra={"youtube_channel_id": youtube_channel_id})
        response = table.get_item(Key={"youtube_channel_id": youtube_channel_id})
        if "Item" in response:
            last_fetched = response["Item"].get("last_fetched_at")
            logger.debug("Last fetched time found", extra={"youtube_channel_id": youtube_channel_id, "last_fetched_at": last_fetched})
            return last_fetched
        logger.debug("No cache entry found", extra={"youtube_channel_id": youtube_channel_id})
        return None
    except Exception as e:
        logger.error("Error getting last fetched time from DynamoDB", extra={"youtube_channel_id": youtube_channel_id, "error": str(e)}, exc_info=True)
        return None


def should_fetch(youtube_channel_id: str) -> bool:
    last_fetched = get_last_fetched_at(youtube_channel_id)
    if not last_fetched:
        logger.info("No cache entry found, should fetch", extra={"youtube_channel_id": youtube_channel_id})
        return True

    current_time = int(datetime.now(timezone.utc).timestamp() * 1000)
    elapsed = (current_time - last_fetched) / 1000

    should_fetch_result = elapsed >= MIN_FETCH_INTERVAL
    logger.info("Rate limit check", extra={"youtube_channel_id": youtube_channel_id, "elapsed_seconds": elapsed, "min_interval": MIN_FETCH_INTERVAL, "should_fetch": should_fetch_result})
    return should_fetch_result


def update_cache(youtube_channel_id: str, etag: Optional[str] = None) -> None:
    current_time = int(datetime.now(timezone.utc).timestamp() * 1000)
    item: Dict[str, Any] = {
        "youtube_channel_id": youtube_channel_id,
        "last_fetched_at": current_time,
    }
    if etag:
        item["etag"] = etag

    logger.debug("Updating cache in DynamoDB", extra={"youtube_channel_id": youtube_channel_id, "last_fetched_at": current_time})
    table.put_item(Item=item)
    logger.debug("Cache updated successfully", extra={"youtube_channel_id": youtube_channel_id})


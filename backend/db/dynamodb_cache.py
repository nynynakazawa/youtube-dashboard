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
        logger.info(f"Getting last fetched time from DynamoDB for channel: {youtube_channel_id}")
        logger.info(f"DynamoDB table name: {DYNAMODB_TABLE_NAME}")
        
        # タイムアウトを避けるため、短いタイムアウトを設定
        import boto3
        from botocore.config import Config
        
        # DynamoDBクライアントにタイムアウト設定を追加
        config = Config(
            connect_timeout=5,
            read_timeout=5,
            retries={'max_attempts': 1}
        )
        dynamodb_client = boto3.client('dynamodb', config=config)
        
        try:
            response = dynamodb_client.get_item(
                TableName=DYNAMODB_TABLE_NAME,
                Key={"youtube_channel_id": {"S": youtube_channel_id}}
            )
            logger.info(f"DynamoDB get_item response received: {response}")
            if "Item" in response:
                last_fetched = response["Item"].get("last_fetched_at", {}).get("N")
                if last_fetched:
                    logger.info(f"Last fetched time found: {last_fetched}")
                    return int(last_fetched)
            logger.info("No cache entry found in DynamoDB")
            return None
        except Exception as db_error:
            logger.error(f"DynamoDB get_item failed: {str(db_error)}", exc_info=True)
            # タイムアウトや接続エラーの場合はNoneを返す（エラーハンドリングで処理）
            return None
    except Exception as e:
        logger.error(f"Error getting last fetched time from DynamoDB: {str(e)}", exc_info=True)
        return None


def should_fetch(youtube_channel_id: str) -> bool:
    try:
        last_fetched = get_last_fetched_at(youtube_channel_id)
        if not last_fetched:
            logger.info(f"No cache entry found, should fetch for channel: {youtube_channel_id}")
            return True

        current_time = int(datetime.now(timezone.utc).timestamp() * 1000)
        elapsed = (current_time - last_fetched) / 1000

        should_fetch_result = elapsed >= MIN_FETCH_INTERVAL
        logger.info(f"Rate limit check: elapsed={elapsed}s, min_interval={MIN_FETCH_INTERVAL}s, should_fetch={should_fetch_result}")
        return should_fetch_result
    except Exception as e:
        logger.error(f"Error in should_fetch, defaulting to True: {str(e)}", exc_info=True)
        # DynamoDBへの接続が失敗した場合は、常にフェッチする
        return True


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


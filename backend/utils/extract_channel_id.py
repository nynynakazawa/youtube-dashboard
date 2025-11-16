import re
from typing import Optional


def extract_channel_id(channel_url_or_id: str) -> Optional[str]:
    """チャンネルIDを抽出。ハンドル名の場合はNoneを返す"""
    if not channel_url_or_id:
        return None

    channel_url_or_id = channel_url_or_id.strip()

    if channel_url_or_id.startswith("UC") and len(channel_url_or_id) == 24:
        return channel_url_or_id

    patterns = [
        r"youtube\.com/channel/([a-zA-Z0-9_-]{24})",
        r"youtube\.com/c/([a-zA-Z0-9_-]+)",
        r"youtube\.com/@([a-zA-Z0-9_-]+)",
        r"youtube\.com/user/([a-zA-Z0-9_-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, channel_url_or_id)
        if match:
            channel_id = match.group(1)
            if channel_id.startswith("UC") and len(channel_id) == 24:
                return channel_id

    return None


def extract_handle(channel_url_or_id: str) -> Optional[str]:
    """ハンドル名（@で始まる）を抽出"""
    if not channel_url_or_id:
        return None

    channel_url_or_id = channel_url_or_id.strip()

    # @で始まるハンドル名を直接指定した場合
    if channel_url_or_id.startswith("@"):
        return channel_url_or_id

    # URLからハンドル名を抽出
    pattern = r"youtube\.com/@([a-zA-Z0-9_-]+)"
    match = re.search(pattern, channel_url_or_id)
    if match:
        return "@" + match.group(1)

    return None


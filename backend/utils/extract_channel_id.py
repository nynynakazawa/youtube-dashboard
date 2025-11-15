import re
from typing import Optional


def extract_channel_id(channel_url_or_id: str) -> Optional[str]:
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


from typing import Any, Dict, Optional
import json

def success_response(data: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(data, ensure_ascii=False, default=str),
    }


def error_response(error_code: str, message: str, status_code: int = 500) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(
            {"error": {"code": error_code, "message": message}},
            ensure_ascii=False,
        ),
    }


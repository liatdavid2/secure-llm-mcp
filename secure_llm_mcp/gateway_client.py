from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from .settings import settings


def build_url(path: str) -> str:
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{settings.gateway_base_url}{path}"


def post_json(path: str, payload: Dict[str, Any], timeout_seconds: float = 120.0) -> Dict[str, Any]:
    url = build_url(path)
    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        return {
            "error": "gateway_http_error",
            "status_code": exc.response.status_code,
            "details": exc.response.text[:1000],
            "url": url,
        }
    except httpx.HTTPError as exc:
        return {
            "error": "gateway_request_failed",
            "details": str(exc),
            "url": url,
        }
    except ValueError as exc:
        return {
            "error": "gateway_invalid_json",
            "details": str(exc),
            "url": url,
        }


def get_json(path: str, timeout_seconds: float = 15.0) -> Dict[str, Any]:
    url = build_url(path)
    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        return {
            "error": "gateway_http_error",
            "status_code": exc.response.status_code,
            "details": exc.response.text[:1000],
            "url": url,
        }
    except httpx.HTTPError as exc:
        return {
            "error": "gateway_request_failed",
            "details": str(exc),
            "url": url,
        }
    except ValueError:
        return {
            "ok": True,
            "status": "reachable_non_json_response",
            "url": url,
        }


def gateway_health() -> Dict[str, Any]:
    health = get_json("/health", timeout_seconds=10.0)
    if "error" not in health:
        return {
            "reachable": True,
            "checked_path": "/health",
            "response": health,
        }

    docs_url = build_url("/docs")
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(docs_url)
            return {
                "reachable": response.status_code < 500,
                "checked_path": "/docs",
                "status_code": response.status_code,
                "url": docs_url,
            }
    except httpx.HTTPError as exc:
        return {
            "reachable": False,
            "checked_path": "/health and /docs",
            "error": str(exc),
            "base_url": settings.gateway_base_url,
        }


def run_chat(payload: Dict[str, Any]) -> Dict[str, Any]:
    return post_json(settings.chat_path, payload, timeout_seconds=180.0)


def call_optional_endpoint(path: Optional[str], payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not path:
        return None
    return post_json(path, payload, timeout_seconds=120.0)

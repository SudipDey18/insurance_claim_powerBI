"""
Viewer Tracking Service Module
Manages unique visitor / viewer counting based on client IP addresses.
Maintains persistent storage in JSON format with thread-safe file operations.
Logs all IP audit trails and access records directly into backend/logs/viewer_audit.log.
"""

import os
import json
import threading
from datetime import datetime
from typing import Dict, Any, Optional

from .config import VIEWERS_DATA_FILE
from .logger import get_viewer_logger

_lock = threading.Lock()
_logger = get_viewer_logger()


def _normalize_ip(ip: Optional[str]) -> str:
    """Normalizes client IP strings to standard format."""
    if not ip:
        return "127.0.0.1"

    clean_ip = ip.strip()
    # Handle comma-separated IPs (e.g. from X-Forwarded-For: client, proxy1, ...)
    if "," in clean_ip:
        clean_ip = clean_ip.split(",")[0].strip()

    # Normalize localhost loopback variants
    if clean_ip in ("::1", "localhost", "0.0.0.0"):
        clean_ip = "127.0.0.1"

    return clean_ip or "127.0.0.1"


def _load_data_unlocked() -> Dict[str, Any]:
    """Loads viewers dictionary from disk. Must be called with lock held."""
    if not os.path.exists(VIEWERS_DATA_FILE):
        return {
            "total_viewers": 0,
            "total_visits": 0,
            "viewers_by_ip": {}
        }

    try:
        with open(VIEWERS_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Corrupt viewer data format")
            if "viewers_by_ip" not in data or not isinstance(data["viewers_by_ip"], dict):
                data["viewers_by_ip"] = {}
            data["total_viewers"] = len(data["viewers_by_ip"])
            data["total_visits"] = sum(
                item.get("visit_count", 1) for item in data["viewers_by_ip"].values()
                if isinstance(item, dict)
            )
            return data
    except Exception:
        return {
            "total_viewers": 0,
            "total_visits": 0,
            "viewers_by_ip": {}
        }


def _save_data_unlocked(data: Dict[str, Any]) -> None:
    """Saves viewers dictionary to disk safely. Must be called with lock held."""
    try:
        os.makedirs(os.path.dirname(VIEWERS_DATA_FILE), exist_ok=True)
        temp_file = f"{VIEWERS_DATA_FILE}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if os.path.exists(temp_file):
            os.replace(temp_file, VIEWERS_DATA_FILE)
    except Exception as e:
        _logger.error(f"Failed to persist viewer tracking data: {e}")


def record_viewer_visit(ip: Optional[str]) -> Dict[str, Any]:
    """
    Records a visit from a client IP address.
    Counts unique viewers by distinct IP address.
    Logs full IP audit details directly into backend/logs/viewer_audit.log.
    Returns only aggregate viewer counts to protect client privacy.
    """
    clean_ip = _normalize_ip(ip)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with _lock:
        data = _load_data_unlocked()
        viewers_by_ip = data.setdefault("viewers_by_ip", {})

        is_new_viewer = clean_ip not in viewers_by_ip
        if is_new_viewer:
            viewers_by_ip[clean_ip] = {
                "visit_count": 1,
                "first_seen": now_str,
                "last_seen": now_str
            }
        else:
            viewers_by_ip[clean_ip]["visit_count"] = viewers_by_ip[clean_ip].get("visit_count", 0) + 1
            viewers_by_ip[clean_ip]["last_seen"] = now_str

        data["total_viewers"] = len(viewers_by_ip)
        data["total_visits"] = sum(v.get("visit_count", 1) for v in viewers_by_ip.values())
        _save_data_unlocked(data)

        ip_record = viewers_by_ip[clean_ip]
        if is_new_viewer:
            _logger.info(
                f"[AUDIT_NEW_VIEWER] Client IP: {clean_ip} | "
                f"Total Unique Viewers: {data['total_viewers']} | "
                f"Total Visits: {data['total_visits']} | "
                f"First Seen: {ip_record['first_seen']}"
            )
        else:
            _logger.info(
                f"[AUDIT_RETURNING_VIEWER] Client IP: {clean_ip} | "
                f"Visits from this IP: {ip_record['visit_count']} | "
                f"Total Unique Viewers: {data['total_viewers']} | "
                f"Total Visits: {data['total_visits']} | "
                f"Last Seen: {ip_record['last_seen']}"
            )

        # Return only aggregate metrics (no IP addresses exposed to front end)
        return {
            "total_viewers": data["total_viewers"],
            "total_visits": data["total_visits"],
            "is_new_viewer": is_new_viewer
        }


def get_viewer_stats(include_audit: bool = False) -> Dict[str, Any]:
    """
    Retrieves current unique viewer counts.
    By default, excludes IP audit logs to avoid exposing client IPs to the frontend.
    """
    with _lock:
        data = _load_data_unlocked()
        result = {
            "total_viewers": data.get("total_viewers", len(data.get("viewers_by_ip", {}))),
            "total_visits": data.get("total_visits", 0)
        }
        if include_audit:
            result["viewers_by_ip"] = data.get("viewers_by_ip", {})
        return result

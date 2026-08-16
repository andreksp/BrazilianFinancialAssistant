import os
import requests
from typing import Optional

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEFAULT_USER = "default"


def process_trade(payload: dict, user_id: str = DEFAULT_USER) -> dict:
    resp = requests.post(
        f"{BASE_URL}/api/trades/process",
        json=payload,
        params={"user_id": user_id},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_trade_history(
    user_id: str = DEFAULT_USER,
    month: Optional[int] = None,
    year: Optional[int] = None,
) -> list:
    params: dict = {"user_id": user_id}
    if month:
        params["month"] = month
    if year:
        params["year"] = year
    resp = requests.get(f"{BASE_URL}/api/trades/history", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_monthly_summary(month: int, year: int, user_id: str = DEFAULT_USER) -> Optional[dict]:
    resp = requests.get(
        f"{BASE_URL}/api/calculations/summary",
        params={"month": month, "year": year, "user_id": user_id},
        timeout=10,
    )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def get_darf_info(month: int, year: int, user_id: str = DEFAULT_USER) -> dict:
    resp = requests.get(
        f"{BASE_URL}/api/calculations/darf",
        params={"month": month, "year": year, "user_id": user_id},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def send_chat(message: str, user_id: str = DEFAULT_USER) -> dict:
    resp = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": message, "user_id": user_id},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

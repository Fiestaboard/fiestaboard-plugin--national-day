"""Display today's national days and fun observances from a bundled dataset."""

from __future__ import annotations

import datetime
import json
import logging
import os
from typing import Any, Dict, List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests

# Bundled dataset path
_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "national_days.json")

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

USER_AGENT = "FiestaBoard National Day Plugin (https://github.com/Fiestaboard/fiestaboard-plugin--national-day)"


def _configured_timezone() -> str:
    """Return FiestaBoard's configured timezone with backward-compatible fallbacks."""
    try:
        from src.config import Config

        return Config.GENERAL_TIMEZONE or Config.TIMEZONE or "UTC"
    except Exception:
        logger.warning("Could not read FiestaBoard timezone; falling back to UTC")
        return "UTC"


def _date_in_timezone(
    timezone_name: str,
    current_time: datetime.datetime | None = None,
) -> datetime.date:
    """Return the calendar date in the requested timezone."""
    try:
        timezone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        logger.warning("Invalid FiestaBoard timezone %r; falling back to UTC", timezone_name)
        timezone = ZoneInfo("UTC")

    now = current_time or datetime.datetime.now(datetime.timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=datetime.timezone.utc)
    return now.astimezone(timezone).date()


class NationalDayPlugin(PluginBase):
    """National Day plugin for FiestaBoard."""

    @property
    def plugin_id(self) -> str:
        return "national_day"

    def fetch_data(self) -> PluginResult:
        try:
            today = _date_in_timezone(_configured_timezone())
            key = f"{today.month:02d}-{today.day:02d}"
            holiday_index = int(self.config.get("holiday_index") or 1) - 1

            with open(_DATA_FILE, encoding="utf-8") as f:
                dataset = json.load(f)

            holidays = dataset.get(key, [])
            if not holidays:
                holidays = ["National Be Yourself Day"]

            if holiday_index >= len(holidays):
                holiday_index = 0

            holiday = str(holidays[holiday_index])
            date_str = today.strftime("%B %-d")
            count = max(0, len(holidays) - 1)

            return PluginResult(
                available=True,
                data={
                    "holiday": holiday,
                    "date": date_str,
                    "count": count,
                },
            )
        except Exception as e:
            logger.exception("Error loading national day data")
            return PluginResult(available=False, error=str(e))

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        return []

    def cleanup(self) -> None:
        pass

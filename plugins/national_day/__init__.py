"""Display today's national days and fun observances from a bundled dataset."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
import requests
import datetime
import json
import os

# Bundled dataset path
_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "national_days.json")

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

USER_AGENT = "FiestaBoard National Day Plugin (https://github.com/Fiestaboard/fiestaboard-plugin--national-day)"


class NationalDayPlugin(PluginBase):
    """National Day plugin for FiestaBoard."""

    @property
    def plugin_id(self) -> str:
        return "national_day"

    def fetch_data(self) -> PluginResult:
        try:
            today = datetime.date.today()
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

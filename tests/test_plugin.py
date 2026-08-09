"""Tests for the national_day plugin."""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

import pytest

from plugins.national_day import NationalDayPlugin
from plugins import national_day
from src.plugins.base import PluginResult

MANIFEST = json.loads("""
{
    "id": "national_day",
    "name": "National Day",
    "version": "0.1.0",
    "settings_schema": {
        "type": "object",
        "properties": {
            "enabled": {
                "type": "boolean",
                "title": "Enabled",
                "default": false
            },
            "holiday_index": {
                "type": "integer",
                "title": "Holiday Position",
                "description": "Which holiday to show when there are multiple (1 = first).",
                "default": 1,
                "minimum": 1,
                "maximum": 5
            },
            "refresh_seconds": {
                "type": "integer",
                "title": "Refresh Interval (seconds)",
                "description": "How often to refresh (once per day is sufficient).",
                "default": 3600,
                "minimum": 3600
            }
        },
        "required": []
    }
}
""")

SAMPLE_RESPONSE = json.loads("""
{
    "09-29": [
        "National Coffee Day",
        "National Biscotti Day",
        "World Heart Day"
    ]
}
""")


@pytest.fixture
def plugin():
    return NationalDayPlugin(MANIFEST)


@pytest.fixture
def configured_plugin():
    p = NationalDayPlugin(MANIFEST)
    p.config = json.loads("""
{
    "holiday_index": 1
}
""")
    return p


class TestNationalDayPlugin:

    def test_plugin_id(self, plugin):
        assert plugin.plugin_id == "national_day"

    def test_manifest_valid(self):
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        with open(manifest_path) as f:
            m = json.load(f)
        for field in ("id", "name", "version"):
            assert field in m

    @patch("plugins.national_day.requests.get")
    def test_fetch_data_success(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.error is None
        assert result.data is not None
        assert "holiday" in result.data, "missing variable: holiday"
        assert "date" in result.data, "missing variable: date"
        assert "count" in result.data, "missing variable: count"

    @pytest.mark.skip(reason="plugin does not use requests.get")
    def test_fetch_data_network_error(self, configured_plugin):
        pass

    @pytest.mark.skip(reason="plugin does not use requests.get")
    def test_fetch_data_bad_json(self, configured_plugin):
        pass
    def test_data_file_exists(self):
        """Bundled national_days.json data file should exist."""
        import plugins.national_day as nd_module
        import os
        data_file = os.path.join(os.path.dirname(nd_module.__file__), "data", "national_days.json")
        assert os.path.isfile(data_file), f"Data file missing: {data_file}"

    def test_date_uses_configured_timezone_at_utc_day_boundary(self):
        now = datetime.datetime(2026, 8, 9, 0, 30, tzinfo=datetime.timezone.utc)

        result = national_day._date_in_timezone("America/Los_Angeles", now)

        assert result == datetime.date(2026, 8, 8)

    def test_fetch_data_uses_configured_local_date(self, configured_plugin):
        local_date = datetime.date(2026, 9, 29)

        with patch(
            "plugins.national_day._configured_timezone",
            return_value="America/Los_Angeles",
        ) as configured_timezone, patch(
            "plugins.national_day._date_in_timezone",
            return_value=local_date,
        ) as date_in_timezone:
            result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.data["date"] == "September 29"
        assert result.data["holiday"] == "National Coffee Day"
        configured_timezone.assert_called_once_with()
        date_in_timezone.assert_called_once_with("America/Los_Angeles")

    def test_configured_timezone_prefers_general_setting(self):
        config = SimpleNamespace(
            GENERAL_TIMEZONE="America/New_York",
            TIMEZONE="America/Los_Angeles",
        )

        with patch("src.config.Config", config):
            assert national_day._configured_timezone() == "America/New_York"

    def test_invalid_timezone_falls_back_to_utc(self):
        now = datetime.datetime(2026, 8, 9, 0, 30, tzinfo=ZoneInfo("UTC"))

        result = national_day._date_in_timezone("Not/A_Timezone", now)

        assert result == datetime.date(2026, 8, 9)

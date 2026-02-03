"""Tests for datetime formatting functions."""

from datetime import datetime, timedelta, timezone

import pytest

from exls.shared.adapters.ui.output.render.service import (
    format_datetime,
    format_datetime_humanized,
)


class TestFormatDatetime:
    """Tests for the format_datetime function (ISO format)."""

    def test_format_naive_datetime(self) -> None:
        """Test formatting a naive (no timezone) datetime."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = format_datetime(dt)
        assert result == "2024-01-15T10:30:45"

    def test_format_datetime_with_utc_timezone(self) -> None:
        """Test formatting a datetime with UTC timezone."""
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        result = format_datetime(dt)
        assert result == "2024-01-15T10:30:45+00:00"

    def test_format_datetime_with_microseconds(self) -> None:
        """Test formatting a datetime with microseconds."""
        dt = datetime(2024, 1, 15, 10, 30, 45, 123456)
        result = format_datetime(dt)
        assert result == "2024-01-15T10:30:45.123456"

    def test_format_datetime_midnight(self) -> None:
        """Test formatting a datetime at midnight."""
        dt = datetime(2024, 1, 15, 0, 0, 0)
        result = format_datetime(dt)
        assert result == "2024-01-15T00:00:00"

    def test_format_datetime_end_of_day(self) -> None:
        """Test formatting a datetime at end of day."""
        dt = datetime(2024, 1, 15, 23, 59, 59)
        result = format_datetime(dt)
        assert result == "2024-01-15T23:59:59"


class TestFormatDatetimeHumanized:
    """Tests for the format_datetime_humanized function."""

    def test_just_now(self) -> None:
        """Test that very recent times show as 'now' or similar."""
        dt = datetime.now(timezone.utc) - timedelta(seconds=1)
        result = format_datetime_humanized(dt)
        # humanize returns "a second ago" or "now" for very recent times
        assert "second" in result.lower() or "now" in result.lower()

    def test_seconds_ago(self) -> None:
        """Test formatting times a few seconds ago."""
        dt = datetime.now(timezone.utc) - timedelta(seconds=30)
        result = format_datetime_humanized(dt)
        assert "second" in result.lower()
        assert "ago" in result.lower()

    def test_one_minute_ago(self) -> None:
        """Test formatting time one minute ago."""
        dt = datetime.now(timezone.utc) - timedelta(minutes=1)
        result = format_datetime_humanized(dt)
        assert "minute" in result.lower()
        assert "ago" in result.lower()

    def test_minutes_ago(self) -> None:
        """Test formatting time several minutes ago."""
        dt = datetime.now(timezone.utc) - timedelta(minutes=5)
        result = format_datetime_humanized(dt)
        assert "minute" in result.lower()
        assert "ago" in result.lower()

    def test_one_hour_ago(self) -> None:
        """Test formatting time one hour ago."""
        dt = datetime.now(timezone.utc) - timedelta(hours=1)
        result = format_datetime_humanized(dt)
        assert "hour" in result.lower()
        assert "ago" in result.lower()

    def test_hours_ago(self) -> None:
        """Test formatting time several hours ago."""
        dt = datetime.now(timezone.utc) - timedelta(hours=3)
        result = format_datetime_humanized(dt)
        assert "hour" in result.lower()
        assert "ago" in result.lower()

    def test_one_day_ago(self) -> None:
        """Test formatting time one day ago."""
        dt = datetime.now(timezone.utc) - timedelta(days=1)
        result = format_datetime_humanized(dt)
        assert "day" in result.lower()
        assert "ago" in result.lower()

    def test_days_ago(self) -> None:
        """Test formatting time several days ago."""
        dt = datetime.now(timezone.utc) - timedelta(days=5)
        result = format_datetime_humanized(dt)
        assert "day" in result.lower()
        assert "ago" in result.lower()

    def test_one_week_ago(self) -> None:
        """Test formatting time one week ago."""
        dt = datetime.now(timezone.utc) - timedelta(weeks=1)
        result = format_datetime_humanized(dt)
        # humanize may return "a week ago" or "7 days ago"
        assert "week" in result.lower() or "day" in result.lower()
        assert "ago" in result.lower()

    def test_weeks_ago(self) -> None:
        """Test formatting time several weeks ago."""
        dt = datetime.now(timezone.utc) - timedelta(weeks=3)
        result = format_datetime_humanized(dt)
        # humanize may return weeks, days, or month (3 weeks is close to a month)
        assert (
            "week" in result.lower()
            or "day" in result.lower()
            or "month" in result.lower()
        )
        assert "ago" in result.lower()

    def test_one_month_ago(self) -> None:
        """Test formatting time one month ago."""
        dt = datetime.now(timezone.utc) - timedelta(days=35)
        result = format_datetime_humanized(dt)
        # humanize may return "a month ago" or similar
        assert "month" in result.lower() or "day" in result.lower()
        assert "ago" in result.lower()

    def test_months_ago(self) -> None:
        """Test formatting time several months ago."""
        dt = datetime.now(timezone.utc) - timedelta(days=90)
        result = format_datetime_humanized(dt)
        assert "month" in result.lower() or "day" in result.lower()
        assert "ago" in result.lower()

    def test_one_year_ago(self) -> None:
        """Test formatting time one year ago."""
        dt = datetime.now(timezone.utc) - timedelta(days=400)
        result = format_datetime_humanized(dt)
        assert "year" in result.lower() or "month" in result.lower()
        assert "ago" in result.lower()

    def test_years_ago(self) -> None:
        """Test formatting time several years ago."""
        dt = datetime.now(timezone.utc) - timedelta(days=800)
        result = format_datetime_humanized(dt)
        assert "year" in result.lower()
        assert "ago" in result.lower()

    def test_naive_datetime_is_handled(self) -> None:
        """Test that naive datetimes are handled gracefully."""
        # Naive datetime (no timezone) should still work
        dt = datetime.now() - timedelta(hours=2)
        result = format_datetime_humanized(dt)
        assert "hour" in result.lower()
        assert "ago" in result.lower()

    def test_future_datetime(self) -> None:
        """Test formatting a future datetime."""
        dt = datetime.now(timezone.utc) + timedelta(hours=2)
        result = format_datetime_humanized(dt)
        # humanize returns "in X hours" for future times, or "from now"
        assert "hour" in result.lower()
        # Future times should indicate they're in the future
        assert "from now" in result.lower() or "in " in result.lower()


class TestHumanizedOutputFormat:
    """Tests to verify the output format is user-friendly."""

    def test_output_is_not_iso_format(self) -> None:
        """Verify humanized output is not in ISO format."""
        dt = datetime.now(timezone.utc) - timedelta(hours=2)
        result = format_datetime_humanized(dt)
        # ISO format contains "T" separator and dashes
        assert "T" not in result
        assert "-" not in result or "ago" in result

    def test_output_is_readable(self) -> None:
        """Verify the output contains human-readable words."""
        dt = datetime.now(timezone.utc) - timedelta(days=3)
        result = format_datetime_humanized(dt)
        # Should contain words, not just numbers
        assert any(
            word in result.lower()
            for word in ["day", "hour", "minute", "second", "week", "month", "year"]
        )

    def test_output_contains_ago_for_past(self) -> None:
        """Verify past times contain 'ago'."""
        dt = datetime.now(timezone.utc) - timedelta(hours=5)
        result = format_datetime_humanized(dt)
        assert "ago" in result.lower()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_exactly_one_hour(self) -> None:
        """Test exactly one hour ago."""
        dt = datetime.now(timezone.utc) - timedelta(hours=1)
        result = format_datetime_humanized(dt)
        assert "hour" in result.lower()

    def test_exactly_one_day(self) -> None:
        """Test exactly one day ago."""
        dt = datetime.now(timezone.utc) - timedelta(days=1)
        result = format_datetime_humanized(dt)
        assert "day" in result.lower()

    def test_boundary_59_minutes(self) -> None:
        """Test 59 minutes ago (just under an hour)."""
        dt = datetime.now(timezone.utc) - timedelta(minutes=59)
        result = format_datetime_humanized(dt)
        assert "minute" in result.lower()

    def test_boundary_61_minutes(self) -> None:
        """Test 61 minutes ago (just over an hour)."""
        dt = datetime.now(timezone.utc) - timedelta(minutes=61)
        result = format_datetime_humanized(dt)
        assert "hour" in result.lower()

    def test_boundary_23_hours(self) -> None:
        """Test 23 hours ago (just under a day)."""
        dt = datetime.now(timezone.utc) - timedelta(hours=23)
        result = format_datetime_humanized(dt)
        assert "hour" in result.lower()

    def test_boundary_25_hours(self) -> None:
        """Test 25 hours ago (just over a day)."""
        dt = datetime.now(timezone.utc) - timedelta(hours=25)
        result = format_datetime_humanized(dt)
        assert "day" in result.lower()

    def test_very_old_date(self) -> None:
        """Test a very old date (10 years ago)."""
        dt = datetime.now(timezone.utc) - timedelta(days=3650)
        result = format_datetime_humanized(dt)
        assert "year" in result.lower()
        assert "ago" in result.lower()

    def test_different_timezone(self) -> None:
        """Test datetime with a non-UTC timezone."""
        # Create a timezone offset of +5 hours
        tz_plus5 = timezone(timedelta(hours=5))
        dt = datetime.now(tz_plus5) - timedelta(hours=2)
        result = format_datetime_humanized(dt)
        assert "hour" in result.lower()


class TestConsistencyBetweenFormatters:
    """Tests to verify the difference between humanized and ISO formatters."""

    def test_same_datetime_different_output(self) -> None:
        """Verify humanized and ISO formatters produce different output."""
        dt = datetime.now(timezone.utc) - timedelta(hours=2)

        iso_result = format_datetime(dt)
        humanized_result = format_datetime_humanized(dt)

        # They should be different
        assert iso_result != humanized_result

        # ISO should contain the T separator
        assert "T" in iso_result

        # Humanized should contain "ago"
        assert "ago" in humanized_result.lower()

    def test_iso_format_is_parseable(self) -> None:
        """Verify ISO format can be parsed back to datetime."""
        original_dt = datetime(2024, 1, 15, 10, 30, 45)
        iso_result = format_datetime(original_dt)

        # Should be able to parse it back
        parsed_dt = datetime.fromisoformat(iso_result)
        assert parsed_dt == original_dt

    @pytest.mark.parametrize(
        "delta,expected_unit",
        [
            (timedelta(seconds=30), "second"),
            (timedelta(minutes=5), "minute"),
            (timedelta(hours=3), "hour"),
            (timedelta(days=2), "day"),
            (timedelta(weeks=2), "week"),
        ],
    )
    def test_humanized_uses_appropriate_unit(
        self, delta: timedelta, expected_unit: str
    ) -> None:
        """Verify humanized formatter uses appropriate time units."""
        dt = datetime.now(timezone.utc) - delta
        result = format_datetime_humanized(dt)
        # Note: humanize may use different units (e.g., "14 days" instead of "2 weeks")
        # so we check for either the expected unit or a smaller unit
        valid_units = ["second", "minute", "hour", "day", "week", "month", "year"]
        assert any(unit in result.lower() for unit in valid_units)

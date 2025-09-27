"""Unit tests for schedule model representing Airtable schedule records."""

from datetime import date, time

import pytest
from pydantic import ValidationError

from src.models.schedule import ScheduleEntry


class TestScheduleEntryModel:
    """Test suite covering validation and serialization of schedule entries."""

    def test_schedule_entry_creation_full(self) -> None:
        """Schedule entry accepts full dataset with all optional fields."""
        entry = ScheduleEntry(
            date=date(2025, 11, 13),
            start_time=time(9, 0),
            end_time=time(10, 30),
            title="Утреннее поклонение",
            description="Общее собрание с молитвой",
            audience="Все участники",
            day_label="Четверг",
            order=1,
            is_active=True,
            location="Главный зал",
        )

        assert entry.date == date(2025, 11, 13)
        assert entry.start_time == time(9, 0)
        assert entry.end_time == time(10, 30)
        assert entry.title == "Утреннее поклонение"
        assert entry.description == "Общее собрание с молитвой"
        assert entry.audience == "Все участники"
        assert entry.day_label == "Четверг"
        assert entry.order == 1
        assert entry.is_active is True
        assert entry.location == "Главный зал"

    def test_schedule_entry_requires_core_fields(self) -> None:
        """Missing required fields should raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleEntry(
                start_time=time(9, 0),
                title="Событие без даты",
            )

        assert "date" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ScheduleEntry(
                date=date(2025, 11, 13),
                title="Событие без времени",
            )

        assert "start_time" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ScheduleEntry(
                date=date(2025, 11, 13),
                start_time=time(9, 0),
            )

        assert "title" in str(exc_info.value)

    def test_schedule_entry_to_airtable_fields(self) -> None:
        """Serialization to Airtable field names preserves required formatting."""
        entry = ScheduleEntry(
            record_id="recSchedule123",
            date=date(2025, 11, 14),
            start_time=time(14, 15),
            end_time=time(15, 0),
            title="Обед",
            description="Шведский стол",
            audience="Команда",
            day_label="Пятница",
            order=5,
            is_active=False,
            location="Столовая",
        )

        fields = entry.to_airtable_fields()

        assert fields == {
            "Date": "2025-11-14",
            "StartTime": "14:15",
            "EndTime": "15:00",
            "Title": "Обед",
            "Description": "Шведский стол",
            "Audience": "Команда",
            "DayLabel": "Пятница",
            "Order": 5,
            "IsActive": False,
            "Location": "Столовая",
        }

    def test_schedule_entry_to_airtable_fields_excludes_none(self) -> None:
        """Optional fields omitted when unset."""
        entry = ScheduleEntry(
            date=date(2025, 11, 15),
            start_time=time(8, 30),
            title="Утренняя зарядка",
            day_label="Суббота",
        )

        fields = entry.to_airtable_fields()

        assert fields == {
            "Date": "2025-11-15",
            "StartTime": "08:30",
            "Title": "Утренняя зарядка",
            "DayLabel": "Суббота",
            "IsActive": True,
        }

    def test_schedule_entry_from_airtable_record(self) -> None:
        """Conversion from Airtable record dictionary populates model correctly."""
        record = {
            "id": "recSchedule999",
            "fields": {
                "Date": "2025-11-16",
                "StartTime": "19:45",
                "EndTime": "21:00",
                "Title": "Вечер прославления",
                "Description": "Заключительное служение",
                "Audience": "Все",
                "DayLabel": "Воскресенье",
                "Order": 12,
                "IsActive": True,
                "Location": "Главный зал",
            },
        }

        entry = ScheduleEntry.from_airtable_record(record)

        assert entry.record_id == "recSchedule999"
        assert entry.date == date(2025, 11, 16)
        assert entry.start_time == time(19, 45)
        assert entry.end_time == time(21, 0)
        assert entry.title == "Вечер прославления"
        assert entry.description == "Заключительное служение"
        assert entry.audience == "Все"
        assert entry.day_label == "Воскресенье"
        assert entry.order == 12
        assert entry.is_active is True
        assert entry.location == "Главный зал"

    def test_schedule_entry_from_airtable_handles_missing_required(self) -> None:
        """Missing Airtable title or date raises ValueError."""
        record_missing_title = {
            "id": "recMissingTitle",
            "fields": {
                "Date": "2025-11-13",
                "StartTime": "10:00",
                "DayLabel": "Четверг",
            },
        }

        with pytest.raises(ValueError) as exc_info:
            ScheduleEntry.from_airtable_record(record_missing_title)

        assert "Title" in str(exc_info.value)

    def test_schedule_entry_time_validation(self) -> None:
        """Start time must be before end time when both provided."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleEntry(
                date=date(2025, 11, 13),
                start_time=time(12, 0),
                end_time=time(11, 0),
                title="Неверное время",
            )

        assert "end_time must be after start_time" in str(exc_info.value)

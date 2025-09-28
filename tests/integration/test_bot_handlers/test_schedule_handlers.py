"""Integration tests for schedule handlers flow."""

import datetime as dt
from unittest.mock import AsyncMock, Mock

import pytest
from telegram import InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes

from src.bot.handlers import schedule_handlers
from src.bot.handlers.schedule_handlers import (
    USER_DATA_LAST_DAY_KEY,
    handle_schedule_callback,
    handle_schedule_command,
)
from src.models.schedule import ScheduleEntry


class StubScheduleService:
    def __init__(self, initial: list[ScheduleEntry], refreshed: list[ScheduleEntry]):
        self.get_schedule_for_date = AsyncMock(return_value=initial)
        self.refresh_schedule_for_date = AsyncMock(return_value=refreshed)


@pytest.fixture
def context():
    ctx = Mock(spec=ContextTypes.DEFAULT_TYPE)
    ctx.user_data = {}
    return ctx


def _command_update():
    update = Mock(spec=Update)
    message = Mock(spec=Message)
    message.reply_text = AsyncMock()
    update.effective_message = message
    update.callback_query = None
    return update


def _callback_update(data: str):
    update = Mock(spec=Update)
    query = Mock()
    query.data = data
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    update.callback_query = query
    update.effective_message = None
    return update, query


def _entry(day: dt.date, hour: int, title: str) -> ScheduleEntry:
    return ScheduleEntry(date=day, start_time=dt.time(hour, 0), title=title)


@pytest.mark.asyncio
async def test_schedule_flow_with_airtable_stub(monkeypatch, context):
    day = dt.date(2025, 11, 13)
    service = StubScheduleService(
        initial=[_entry(day, 9, "Opening Service")],
        refreshed=[_entry(day, 10, "Updated Talk")],
    )
    monkeypatch.setattr(schedule_handlers, "get_schedule_service", lambda: service)

    # Command entry should prompt for day selection and reset user state
    cmd_update = _command_update()
    await handle_schedule_command(cmd_update, context)
    cmd_update.effective_message.reply_text.assert_called_once()
    assert USER_DATA_LAST_DAY_KEY not in context.user_data

    # Selecting day fetches schedule and stores last selected day
    day_update, day_query = _callback_update(f"schedule:{day.isoformat()}")
    await handle_schedule_callback(day_update, context)
    service.get_schedule_for_date.assert_awaited_once_with(day)
    assert context.user_data[USER_DATA_LAST_DAY_KEY] == day.isoformat()
    day_query.edit_message_text.assert_called_once()
    header_text = day_query.edit_message_text.call_args.args[0].splitlines()[0]
    assert "2025-11-13" in header_text

    # Refresh should fetch new data and update output text
    refresh_update, refresh_query = _callback_update("schedule:refresh")
    await handle_schedule_callback(refresh_update, context)
    service.refresh_schedule_for_date.assert_awaited_once_with(day)
    refreshed_text = refresh_query.edit_message_text.call_args.args[0]
    assert "Updated Talk" in refreshed_text
    assert isinstance(
        refresh_query.edit_message_text.call_args.kwargs["reply_markup"],
        InlineKeyboardMarkup,
    )


@pytest.mark.asyncio
async def test_schedule_refresh_without_selected_day_shows_prompt(context):
    update, query = _callback_update("schedule:refresh")

    await handle_schedule_callback(update, context)

    query.edit_message_text.assert_called_once()
    assert "Выберите день" in query.edit_message_text.call_args.args[0]
    assert isinstance(
        query.edit_message_text.call_args.kwargs["reply_markup"], InlineKeyboardMarkup
    )

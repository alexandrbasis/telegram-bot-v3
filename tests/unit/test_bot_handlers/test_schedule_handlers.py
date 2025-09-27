"""Unit tests for schedule command handlers."""

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


@pytest.fixture
def mock_context():
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context


@pytest.fixture
def mock_message():
    message = Mock(spec=Message)
    message.reply_text = AsyncMock()
    message.edit_text = AsyncMock()
    return message


@pytest.fixture
def mock_update_with_message(mock_message):
    update = Mock(spec=Update)
    update.effective_message = mock_message
    update.callback_query = None
    return update


@pytest.mark.asyncio
async def test_handle_schedule_command_prompts_for_day(
    mock_context, mock_update_with_message
):
    mock_context.user_data[USER_DATA_LAST_DAY_KEY] = "2025-11-13"

    await handle_schedule_command(mock_update_with_message, mock_context)

    assert USER_DATA_LAST_DAY_KEY not in mock_context.user_data
    mock_update_with_message.effective_message.reply_text.assert_called_once()
    kwargs = mock_update_with_message.effective_message.reply_text.call_args.kwargs
    assert isinstance(kwargs["reply_markup"], InlineKeyboardMarkup)


def _build_callback_update(data: str):
    query = Mock()
    query.data = data
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    update = Mock(spec=Update)
    update.callback_query = query
    update.effective_message = None
    return update, query


def _schedule_entry(day: dt.date, hour: int, title: str) -> ScheduleEntry:
    return ScheduleEntry(date=day, start_time=dt.time(hour, 0), title=title)


@pytest.mark.asyncio
async def test_handle_schedule_callback_with_valid_day(monkeypatch, mock_context):
    day = dt.date(2025, 11, 13)
    update, query = _build_callback_update(f"schedule:{day.isoformat()}")

    service = Mock()
    service.get_schedule_for_date = AsyncMock(
        return_value=[_schedule_entry(day, 9, "Opening")]
    )
    monkeypatch.setattr(schedule_handlers, "get_schedule_service", lambda: service)

    await handle_schedule_callback(update, mock_context)

    service.get_schedule_for_date.assert_awaited_once()
    assert mock_context.user_data[USER_DATA_LAST_DAY_KEY] == day.isoformat()
    query.edit_message_text.assert_called_once()
    call = query.edit_message_text.call_args
    assert "09:00" in call.args[0]
    assert isinstance(call.kwargs["reply_markup"], InlineKeyboardMarkup)


@pytest.mark.asyncio
async def test_handle_schedule_callback_invalid_date(mock_context):
    update, query = _build_callback_update("schedule:not-a-date")

    await handle_schedule_callback(update, mock_context)

    query.edit_message_text.assert_called_once()
    assert "Некорректная дата" in query.edit_message_text.call_args.args[0]


@pytest.mark.asyncio
async def test_handle_schedule_callback_refresh_without_selection(mock_context):
    update, query = _build_callback_update("schedule:refresh")

    await handle_schedule_callback(update, mock_context)

    query.edit_message_text.assert_called_once()
    assert "Выберите день" in query.edit_message_text.call_args.args[0]


@pytest.mark.asyncio
async def test_handle_schedule_callback_refresh_with_selection(
    monkeypatch, mock_context
):
    day = dt.date(2025, 11, 14)
    mock_context.user_data[USER_DATA_LAST_DAY_KEY] = day.isoformat()
    update, query = _build_callback_update("schedule:refresh")

    service = Mock()
    service.refresh_schedule_for_date = AsyncMock(
        return_value=[_schedule_entry(day, 10, "Updated")]
    )
    monkeypatch.setattr(schedule_handlers, "get_schedule_service", lambda: service)

    await handle_schedule_callback(update, mock_context)

    service.refresh_schedule_for_date.assert_awaited_once_with(day)
    call = query.edit_message_text.call_args
    assert "10:00" in call.args[0]
    assert isinstance(call.kwargs["reply_markup"], InlineKeyboardMarkup)


@pytest.mark.asyncio
async def test_handle_schedule_callback_service_error(monkeypatch, mock_context):
    day = dt.date(2025, 11, 13)
    update, query = _build_callback_update(f"schedule:{day.isoformat()}")

    service = Mock()
    service.get_schedule_for_date = AsyncMock(side_effect=RuntimeError("boom"))
    monkeypatch.setattr(schedule_handlers, "get_schedule_service", lambda: service)

    await handle_schedule_callback(update, mock_context)

    query.edit_message_text.assert_called_once()
    assert "Не удалось загрузить" in query.edit_message_text.call_args.args[0]
    assert USER_DATA_LAST_DAY_KEY not in mock_context.user_data

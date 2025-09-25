"""Tests for admin command handlers."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Update

from src.bot.handlers.admin_handlers import (
    handle_auth_refresh_command,
    handle_logging_toggle_command,
)


@pytest.fixture
def mock_update():
    update = Mock(spec=Update)
    message = Mock()
    message.reply_text = AsyncMock()
    update.effective_message = message
    user = Mock()
    user.id = 123
    user.username = "admin"
    update.effective_user = user
    return update


@pytest.fixture
def mock_context():
    context = Mock()
    context.args = []
    context.bot_data = {"settings": Mock()}
    return context


@patch("src.bot.handlers.admin_handlers.is_admin_user", return_value=False)
@pytest.mark.asyncio
async def test_logging_toggle_denies_non_admin(
    mock_is_admin, mock_update, mock_context
):
    await handle_logging_toggle_command(mock_update, mock_context)

    mock_is_admin.assert_called_once()
    mock_update.effective_message.reply_text.assert_called_once()
    assert "нет прав" in mock_update.effective_message.reply_text.call_args[0][0]


@patch("src.bot.handlers.admin_handlers.is_admin_user", return_value=True)
@patch(
    "src.bot.handlers.admin_handlers.is_user_interaction_logging_enabled",
    return_value=True,
)
@pytest.mark.asyncio
async def test_logging_toggle_status_report(
    mock_is_enabled, mock_is_admin, mock_update, mock_context
):
    await handle_logging_toggle_command(mock_update, mock_context)

    mock_is_enabled.assert_called_once()
    mock_update.effective_message.reply_text.assert_called_once()
    message = mock_update.effective_message.reply_text.call_args[0][0]
    assert "Логирование взаимодействий" in message


@patch("src.bot.handlers.admin_handlers.set_user_interaction_logging_enabled")
@patch("src.bot.handlers.admin_handlers.is_admin_user", return_value=True)
@pytest.mark.asyncio
async def test_logging_toggle_enable(
    mock_is_admin, mock_set_logging, mock_update, mock_context
):
    mock_context.args = ["on"]

    await handle_logging_toggle_command(mock_update, mock_context)

    mock_set_logging.assert_called_once_with(True)
    mock_update.effective_message.reply_text.assert_called_once()
    assert "включено" in mock_update.effective_message.reply_text.call_args[0][0]


@patch("src.bot.handlers.admin_handlers.set_user_interaction_logging_enabled")
@patch("src.bot.handlers.admin_handlers.is_admin_user", return_value=True)
@pytest.mark.asyncio
async def test_logging_toggle_disable(
    mock_is_admin, mock_set_logging, mock_update, mock_context
):
    mock_context.args = ["off"]

    await handle_logging_toggle_command(mock_update, mock_context)

    mock_set_logging.assert_called_once_with(False)
    mock_update.effective_message.reply_text.assert_called_once()
    assert "отключено" in mock_update.effective_message.reply_text.call_args[0][0]


@patch("src.bot.handlers.admin_handlers.is_admin_user", return_value=False)
@pytest.mark.asyncio
async def test_auth_refresh_denies_non_admin(
    mock_is_admin, mock_update, mock_context
):
    """Test auth refresh command denies access to non-admin users."""
    await handle_auth_refresh_command(mock_update, mock_context)

    mock_is_admin.assert_called_once_with(123, mock_context.bot_data["settings"])
    mock_update.effective_message.reply_text.assert_called_once()
    assert "нет прав" in mock_update.effective_message.reply_text.call_args[0][0]


@patch("src.bot.handlers.admin_handlers.invalidate_role_cache")
@patch("src.bot.handlers.admin_handlers.is_admin_user", return_value=True)
@pytest.mark.asyncio
async def test_auth_refresh_allows_admin_user(
    mock_is_admin, mock_invalidate_cache, mock_update, mock_context
):
    """Test auth refresh command allows access to admin users and clears cache."""
    await handle_auth_refresh_command(mock_update, mock_context)

    mock_is_admin.assert_called_once_with(123, mock_context.bot_data["settings"])
    mock_invalidate_cache.assert_called_once()
    mock_update.effective_message.reply_text.assert_called_once()

    message = mock_update.effective_message.reply_text.call_args[0][0]
    assert "обновлен" in message
    assert "перезагружены" in message


@pytest.mark.asyncio
async def test_auth_refresh_handles_missing_settings(mock_update):
    """Test auth refresh command handles missing settings gracefully."""
    mock_context = Mock()
    mock_context.bot_data = {}  # No settings

    await handle_auth_refresh_command(mock_update, mock_context)

    mock_update.effective_message.reply_text.assert_called_once()
    message = mock_update.effective_message.reply_text.call_args[0][0]
    assert "недоступны" in message


@pytest.mark.asyncio
async def test_auth_refresh_handles_missing_user():
    """Test auth refresh command handles missing user gracefully."""
    update = Mock(spec=Update)
    update.effective_message = None
    update.effective_user = None

    context = Mock()
    context.bot_data = {"settings": Mock()}

    result = await handle_auth_refresh_command(update, context)

    # Should return without doing anything
    assert result is None


@pytest.mark.asyncio
async def test_auth_refresh_handles_missing_message():
    """Test auth refresh command handles missing message gracefully."""
    update = Mock(spec=Update)
    update.effective_message = None
    update.effective_user = Mock()
    update.effective_user.id = 123

    context = Mock()
    context.bot_data = {"settings": Mock()}

    result = await handle_auth_refresh_command(update, context)

    # Should return without doing anything
    assert result is None

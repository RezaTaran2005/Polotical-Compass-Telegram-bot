from __future__ import annotations
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from config import REQUIRED_CHANNEL_ID

logger = logging.getLogger(__name__)

async def is_member(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(
            chat_id=REQUIRED_CHANNEL_ID,
            user_id=user_id,
        )
        # Statuses that mean "user is in the channel"
        return member.status in ("member", "administrator", "creator")
    except (TelegramForbiddenError, TelegramBadRequest) as exc:
        logger.warning(
            "Could not check membership for user %d: %s. "
            "Make sure the bot is an admin of the required channel and "
            "REQUIRED_CHANNEL_ID is correct.",
            user_id,
            exc,
        )
        return True

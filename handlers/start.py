

from __future__ import annotations
import logging
from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from keyboards.inline import join_channel_keyboard, start_test_keyboard
from services.membership import is_member


logger = logging.getLogger(__name__)
router = Router(name="start")



@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot) -> None:
    """Entry point for every new or returning user."""
    user = message.from_user
    logger.info("User %d (%s) triggered /start", user.id, user.full_name)

    if await is_member(bot, user.id):
        await _show_welcome(message, user.full_name, send_new=True)
    else:
        await _show_join_prompt(message, send_new=True)


@router.callback_query(F.data == "check_membership")
async def cb_check_membership(callback: CallbackQuery, bot: Bot) -> None:
    """Re-validate membership when the user taps 'I Joined ✅'."""
    user = callback.from_user

    if await is_member(bot, user.id):
        await callback.message.edit_text(
            text=_welcome_text(user.full_name),
            reply_markup=start_test_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer("Welcome! 🎉")
    else:
        await callback.answer(
            "You haven't joined yet. Please join the channel first! 📢",
            show_alert=True,
        )


def _welcome_text(name: str) -> str:
    return (
         f"👋 خوش آمدید، <b>{name}</b>!\n\n"
        "شما در حال شروع <b>آزمون قطب‌نما سیاسی</b> هستید.\n\n"
        "این آزمون شامل سری‌ای از عبارات است. برای هر کدام، "
        "میزان موافقت یا مخالفت خود را انتخاب کنید. "
        "پاسخ درست یا غلط وجود ندارد — فقط راستگو باشید!\n\n"
        "🕐 آزمون تقریباً <b>۳–۵ دقیقه</b> طول می‌کشد.\n\n"
        "وقتی آماده‌اید روی <b>شروع آزمون</b> کلیک کنید."
    )


def _join_prompt_text() -> str:
    return (
        "🔒 <b>عضویت الزامی است</b>\n\n"
        "برای استفاده ابتدا در کامال عضو شوید\n\n"
        "بعد از پیوستن، روی <b>پیوستم ✅</b> کلیک کنید."
    )


async def _show_welcome(message: Message, name: str, *, send_new: bool) -> None:
    text = _welcome_text(name)
    if send_new:
        await message.answer(text, reply_markup=start_test_keyboard(), parse_mode="HTML")
    else:
        await message.edit_text(text, reply_markup=start_test_keyboard(), parse_mode="HTML")


async def _show_join_prompt(message: Message, *, send_new: bool) -> None:
    text = _join_prompt_text()
    if send_new:
        await message.answer(text, reply_markup=join_channel_keyboard(), parse_mode="HTML")
    else:
        await message.edit_text(text, reply_markup=join_channel_keyboard(), parse_mode="HTML")

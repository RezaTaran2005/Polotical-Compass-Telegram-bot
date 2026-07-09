from __future__ import annotations
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ANSWER_LABELS, REQUIRED_CHANNEL_LINK
# Membership gate keyboards

def join_channel_keyboard() -> InlineKeyboardMarkup:
    """Two buttons: open the channel link + re-check membership."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="عضویت درکانال 📢",
            url=REQUIRED_CHANNEL_LINK,
        ),
        InlineKeyboardButton(
            text="عضو شدم ✅",
            callback_data="check_membership",
        ),
    )
    return builder.as_markup()


# Welcome keyboards
def start_test_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🧭شروع آزمون", callback_data="start_test")
    return builder.as_markup()


# Quiz question keyboards

def answer_keyboard(
    question_index: int,
    total_questions: int,
    current_answer: str | None = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    #  Answer buttons (one per row for readability on mobile) 
    for key, label in ANSWER_LABELS.items():
        # Prefix a checkmark to the currently selected answer.
        display = f"✓ {label}" if key == current_answer else label
        builder.button(
            text=display,
            callback_data=f"answer:{key}",
        )

    builder.adjust(1)

    #Navigation row 
    nav_buttons: list[InlineKeyboardButton] = []

    if question_index > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️ سوال قبل",
                callback_data="quiz:prev",
            )
        )

    nav_buttons.append(
        InlineKeyboardButton(
            text="❌لغو آزمون",
            callback_data="quiz:cancel",
        )
    )

    builder.row(*nav_buttons)

    return builder.as_markup()



def after_result_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 آزمون دوباره", callback_data="start_test")
    return builder.as_markup()


def cancel_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ بله،انصراف بده", callback_data="quiz:cancel_confirm")
    builder.button(text="⬅️ ادامه آزمون", callback_data="quiz:cancel_abort")
    builder.adjust(2)
    return builder.as_markup()

from __future__ import annotations
import asyncio
import logging
from aiogram import Bot, F, Router
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from keyboards.inline import (
    after_result_keyboard,
    answer_keyboard,
    cancel_confirm_keyboard,
    start_test_keyboard,
)
from services.chart import generate_compass_image
from services.question_loader import Question, load_questions
from services.scoring import compute_totals, get_quadrant_label, normalise
from utils.user_state import (
    UserSession,
    create_session,
    delete_session,
    get_session,
)

logger = logging.getLogger(__name__)
router = Router(name="quiz")


# Helpers

def _question_text(question: Question, index: int, total: int) -> str:
    progress_bar = _build_progress_bar(index, total)
    return (
        f"<b>Question {index + 1} of {total}</b>\n"
        f"{progress_bar}\n\n"
        f"📋 <i>{question.text}</i>\n\n"
        "میزان موافقت یا مخالفت را انتخاب کنید:"
    )


def _build_progress_bar(index: int, total: int, width: int = 10) -> str:
    filled = round((index / total) * width)
    bar = "█" * filled + "░" * (width - filled)
    pct = round((index / total) * 100)
    return f"[{bar}] {pct}%"


async def _send_or_edit_question(
    callback: CallbackQuery,
    session: UserSession,
    questions: list[Question],
) -> None:
    q = questions[session.current_index]
    text = _question_text(q, session.current_index, len(questions))
    markup = answer_keyboard(
        question_index=session.current_index,
        total_questions=len(questions),
        current_answer=session.answers.get(q.id),
    )

    try:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        session.active_message_id = callback.message.message_id
    except Exception:
        # Fallback: send a new message
        sent = await callback.message.answer(text, reply_markup=markup, parse_mode="HTML")
        session.active_message_id = sent.message_id


# Start / restart test

@router.callback_query(F.data == "start_test")
async def cb_start_test(callback: CallbackQuery) -> None:
    questions = load_questions()
    session = create_session(callback.from_user.id)
    session.current_index = 0

    q = questions[0]
    text = _question_text(q, 0, len(questions))
    markup = answer_keyboard(0, len(questions))

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    session.active_message_id = callback.message.message_id
    await callback.answer()

# Answer a question

@router.callback_query(F.data.startswith("answer:"))
async def cb_answer(callback: CallbackQuery, bot: Bot) -> None:
    user_id = callback.from_user.id
    session = get_session(user_id)

    if session is None:
        await callback.answer("Session expired. Please /start again.", show_alert=True)
        return

    questions = load_questions()
    answer_key = callback.data.split(":", 1)[1]   # e.g. "strongly_agree"
    current_q = questions[session.current_index]

    # Store / overwrite the answer for this question
    session.answers[current_q.id] = answer_key

    await callback.answer()

    next_index = session.current_index + 1

    if next_index >= len(questions):
        await _finish_quiz(callback, bot, session, questions)
    else:
        session.current_index = next_index
        await _send_or_edit_question(callback, session, questions)


# Navigate backwards

@router.callback_query(F.data == "quiz:prev")
async def cb_prev(callback: CallbackQuery) -> None:
    """Go back one question."""
    user_id = callback.from_user.id
    session = get_session(user_id)

    if session is None:
        await callback.answer("Session expired. Please /start again.", show_alert=True)
        return

    if session.current_index > 0:
        session.current_index -= 1

    questions = load_questions()
    await _send_or_edit_question(callback, session, questions)
    await callback.answer()


# Cancel flow

@router.callback_query(F.data == "quiz:cancel")
async def cb_cancel(callback: CallbackQuery) -> None:
    """Show a cancel-confirmation prompt."""
    await callback.message.edit_text(
        "⚠️ <b>Are you sure you want to cancel the test?</b>\n\n"
        "Your progress will be lost.",
        reply_markup=cancel_confirm_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "quiz:cancel_confirm")
async def cb_cancel_confirm(callback: CallbackQuery) -> None:
    delete_session(callback.from_user.id)
    await callback.message.edit_text(
        "❌ Test cancelled.\n\nPress <b>Start Test</b> whenever you're ready to try again.",
        reply_markup=start_test_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer("Test cancelled.")


@router.callback_query(F.data == "quiz:cancel_abort")
async def cb_cancel_abort(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    session = get_session(user_id)

    if session is None:
        await callback.answer("Session expired. Please /start again.", show_alert=True)
        return

    questions = load_questions()
    await _send_or_edit_question(callback, session, questions)
    await callback.answer()


# Finish quiz & send result

async def _finish_quiz(
    callback: CallbackQuery,
    bot: Bot,
    session: UserSession,
    questions: list[Question],
) -> None:
    # ── Scoring ───────────────────────────────────────────────────────────────
    raw_x, raw_y = compute_totals(questions, session.answers)
    norm_x, norm_y = normalise(raw_x, raw_y, questions)
    quadrant = get_quadrant_label(norm_x, norm_y)

    # ── Prepare a "rendering…" placeholder while the chart is being generated ─
    await callback.message.edit_text(
        "⏳ Calculating your result…",
        reply_markup=None,
    )

    # ── Generate chart in a thread pool to avoid blocking the event loop ──────
    loop = asyncio.get_event_loop()
    image_bytes = await loop.run_in_executor(
        None, generate_compass_image, norm_x, norm_y
    )

    #  Build result caption 
    caption = (
        "🧭 <b>Your Political Compass Result</b>\n\n"
        f"📊 <b>Economic axis (Left/Right):</b>  <code>{norm_x:+.2f}</code>\n"
        f"🏛 <b>Social axis (Auth/Lib):</b>     <code>{norm_y:+.2f}</code>\n\n"
        f"🗺 <b>Your position:</b>  <b>{quadrant}</b>\n\n"
    )

    #  Send compass image --
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=BufferedInputFile(image_bytes, filename="political_compass.png"),
        caption=caption,
        parse_mode="HTML",
        reply_markup=after_result_keyboard(),
    )





    try:
        await callback.message.delete()
    except Exception:
        pass

    delete_session(callback.from_user.id)
    logger.info(
        "User %d completed the quiz: x=%.2f y=%.2f (%s)",
        callback.from_user.id, norm_x, norm_y, quadrant,
    )

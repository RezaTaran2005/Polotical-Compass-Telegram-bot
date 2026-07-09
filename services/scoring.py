from __future__ import annotations

from services.question_loader import Question

# Mapping from callback_data answer key → raw multiplier
ANSWER_VALUES: dict[str, int] = {
    "strongly_disagree": -2,
    "disagree":          -1,
    "agree":             +1,
    "strongly_agree":    +2,
}


def calculate_score(
    answer_key: str,
    question: Question,
) -> float:
    answer_value = ANSWER_VALUES[answer_key]
    return float(answer_value * question.units * question.direction)


def compute_totals(
    questions: list[Question],
    answers: dict[int, str],
) -> tuple[float, float]:
    raw_x = 0.0
    raw_y = 0.0

    for q in questions:
        answer_key = answers.get(q.id)
        if answer_key is None:
            continue  
        score = calculate_score(answer_key, q)
        if q.axis == "x":
            raw_x += score
        else:
            raw_y += score

    return raw_x, raw_y


def max_possible_score(questions: list[Question], axis: str) -> float:
    return sum(q.units * 2 for q in questions if q.axis == axis)


def normalise(
    raw_x: float,
    raw_y: float,
    questions: list[Question],
) -> tuple[float, float]:
    max_x = max_possible_score(questions, "x") or 1  
    max_y = max_possible_score(questions, "y") or 1

    norm_x = round((raw_x / max_x) * 10, 2)
    norm_y = round((raw_y / max_y) * 10, 2)

    # Clamp to [-10, +10] just in case of floating-point drift
    norm_x = max(-10.0, min(10.0, norm_x))
    norm_y = max(-10.0, min(10.0, norm_y))

    return norm_x, norm_y


def get_quadrant_label(x: float, y: float) -> str:
    horizontal = "Right" if x >= 0 else "Left"
    vertical   = "Authoritarian" if y >= 0 else "Libertarian"
    return f"{horizontal} {vertical}"

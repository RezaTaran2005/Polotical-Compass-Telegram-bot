
import os



BOT_TOKEN: str = 

REQUIRED_CHANNEL_USERNAME: str = ""
REQUIRED_CHANNEL_LINK: str = "https://t.me/"

REQUIRED_CHANNEL_ID: int = 


#Questions file 
QUESTIONS_FILE: str = os.path.join(os.path.dirname(__file__), "questions.json")

# Answer value mapping 
ANSWER_VALUES: dict[str, int] = {
    "strongly_disagree": -2,
    "disagree":          -1,
    "agree":             +1,
    "strongly_agree":    +2,
}

ANSWER_LABELS: dict[str, str] = {
    "strongly_disagree": "🔴 کاملاً مخالفم",
    "disagree":          "🟠 مخالفم",
    "agree":             "🟢 موافقم",
    "strongly_agree":    "🔵 کاملاً موافقم",
}

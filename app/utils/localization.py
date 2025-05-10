messages = {
    "danger": {
        "zh": "主人，当心危险",
        "en": "Master, beware of danger",
    },
    "safe": {
        "zh": "主人，很安全",
        "en": "Master, very safe",
    },
    "risk": {
        "zh": "主人，有风险",
        "en": "Master, risk",
    },
    "unknow": {
        "zh": "主人，没有查到相关信息",
        "en": "Master, no relevant information found",
    }
}

def get_message(key: str, lang: str = "zh") -> str:
    return messages.get(key, {}).get(lang, "")

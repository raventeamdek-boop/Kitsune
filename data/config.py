from environs import Env

env = Env()
env.read_env()


def normalize_logs_chat(raw_chat_id: str) -> str:
    value = str(raw_chat_id).strip()
    if value.startswith("-100"):
        return value
    if value.isdigit():
        return f"-100{value}"
    return value


BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
LOGS_CHAT = normalize_logs_chat(env.str("logs_chat", "-1003990572502"))
IP = env.str("ip", "localhost")
ADMIN_PANEL_PASSWORD = env.str("admin_password", "Aa12345687!")

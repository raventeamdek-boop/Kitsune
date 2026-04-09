from utils.db_api.baza import *


def profile_text(userid, name):
    info = get_user_info(userid)
    orders_count = len(get_user_buys(userid))
    reg_date = info[3] if info and len(info) > 3 else "Неизвестно"
    return (
        f"👨‍💻 <b>Профиль:</b> <code>{name}</code>\n"
        f"🆔 <code>{userid}</code>\n\n"
        f"📦 <b>Кол-во заказов:</b> <code>{orders_count} шт.</code>\n\n"
        f"📅 <b>Дата регистрации:</b> <code>{reg_date}</code>"
    )

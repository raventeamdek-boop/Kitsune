from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db_api.baza import get_busket_info


def start_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text='📃 Правила магазина', url='https://telegra.ph/Flower-Shop-Rules-04-09'),
        InlineKeyboardButton(text='☑️ Ознакомлен', callback_data='accept_rules'),
    )
    return kb


def profile_but(userid):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text=f'🗑 Корзина({len(get_busket_info(userid))} шт.)', callback_data='basket'),
        InlineKeyboardButton(text='🛒 Мои заказы', callback_data='my_buys'),
    )
    return kb


def cancel_payment():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='💢 Отменить', callback_data='cancel_payment'))
    return kb


def busket_but(info):
    kb = InlineKeyboardMarkup(row_width=1)
    for i in info:
        kb.add(InlineKeyboardButton(text=f'🧿 Товар #{i[0]}', callback_data=f'staff+{i[0]}'))
    kb.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_profile'))
    return kb


def support_but():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text='🤵‍♂️ Менеджер по продажам', url='https://t.me/flower_shop_manager'),
        InlineKeyboardButton(text='👨‍⚖️ Администрация магазина', url='https://t.me/flower_admin_bot'),
    )
    return kb


def svyr_but():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text='📮 Канал антишвыр', url='https://t.me/mexican_cartel'),
        InlineKeyboardButton(text='💬 Чат антишвыр', url='https://t.me/cartel_adminbot'),
    )
    return kb

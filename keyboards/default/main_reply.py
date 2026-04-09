from aiogram.types import ReplyKeyboardMarkup
from lists_bot import city_list, staff_list


def main_menu():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(
        '💐 Заказать цветы',
        '💼 Профиль',
        '👨‍⚖️ Поддержка',
    )
    return kb


def city_but():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for city in city_list:
        kb.add(city)
    kb.add('📂 Главное меню')
    return kb


def staff_but():
    kb = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for staff in staff_list:
        kb.add(staff)
    kb.add('📂 Главное меню')
    return kb


def buy_menu():
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add('♻️ Авто-доставка')
    kb.add('📂 Главное меню')
    return kb

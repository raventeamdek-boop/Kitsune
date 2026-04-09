from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_but():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text='🔔 Рассылка', callback_data='spam'),
        InlineKeyboardButton(text='📊 Статистика', callback_data='stata'),
        InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings'),
        InlineKeyboardButton(text='🧛‍♀️ Скрыть', callback_data='hide_adm'),
    )
    return kb


def spam_types():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text='💬 Текстом', callback_data='spam_text'),
        InlineKeyboardButton(text='🖼 Картинкой', callback_data='spam_pic'),
        InlineKeyboardButton(text='📹 Видео', callback_data='spam_video'),
        InlineKeyboardButton(text='🎞 Гифкой', callback_data='spam_gif'),
        InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_admin'),
    )
    return kb


def cancel_but():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='💢 Отменить', callback_data='cansel_spam'))
    return kb


def spam_withot_but():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='💢 Понятно', callback_data='close_spam'))
    return kb


def spam_with_but(text, url):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text=text, url=url),
        InlineKeyboardButton(text='💢 Понятно', callback_data='close_spam'),
    )
    return kb

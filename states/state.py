from aiogram.dispatcher.filters.state import State, StatesGroup


class BALANCE(StatesGroup):
    summa = State()
    message_id = State()


class MAKE_DEAL(StatesGroup):
    rayon = State()
    staff = State()


class SPAM_DATA(StatesGroup):
    text = State()
    photo = State()
    animation = State()
    video = State()
    caption = State()
    but_info = State()
    message_id = State()
    check_spam_type = State()
    confirm_spam = State()


class ADMIN_INFO(StatesGroup):
    message_id = State()
    p2p = State()
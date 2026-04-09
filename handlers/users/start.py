from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from datetime import datetime

from data.config import LOGS_CHAT
from keyboards.default.main_reply import main_menu
from keyboards.inline.main_inline import start_menu
from loader import dp, bot
from utils.db_api.baza import check_new_user, add_new_user


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    userid = message.chat.id
    with open('photos/cartel.jpg', 'rb') as cartel:
        if check_new_user(userid):
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            add_new_user(userid, date)
            await message.answer_photo(
                photo=cartel,
                caption=(
                    f"<b>{message.from_user.full_name}, вас приветствует Kitsune Shop</b> 🌸\n\n"
                    "👨‍💻 <code>Ознакомьтесь с правилами магазина!</code>"
                ),
                reply_markup=start_menu(),
            )
            await bot.send_message(
                chat_id=LOGS_CHAT,
                text=(
                    f"🐘 В нашем боте новый пользователь: "
                    f"<a href=\"tg://user?id={message.chat.id}\">{message.from_user.full_name}</a>\n"
                    f"└@{message.from_user.username}"
                ),
            )
        else:
            await message.answer_photo(
                photo=cartel,
                caption=f"<b>{message.from_user.full_name}, приветствуем вас снова в Kitsune Shop</b> 🌸",
                reply_markup=main_menu(),
            )

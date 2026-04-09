import asyncio
import logging
import re
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentType

from bot_text import *
from converter_time import *
from data.config import *
from generate_id import *
from keyboards.default.main_reply import buy_menu, city_but, main_menu, staff_but
from keyboards.inline.main_admin import *
from keyboards.inline.main_inline import *
from lists_bot import *
from loader import dp, bot
from states.state import *
from utils.admin_auth import grant_admin_access, has_admin_access


def is_admin(user_id: int) -> bool:
    return has_admin_access(user_id) or str(user_id) in ADMINS


def get_flower_description(staff_text: str) -> str:
    qty_match = re.search(r"(\d+(?:[.,]\d+)?)", staff_text)
    qty = qty_match.group(1).replace(",", ".") if qty_match else ""
    if qty == "1":
        return "🌼 <b>Описание:</b> Базовый букет 1 кг. Классический вариант на каждый день."
    if qty == "5":
        return "🌷 <b>Описание:</b> Набор 5 кг. Более объемный букет для особого случая."
    if qty == "10":
        return "🌹 <b>Описание:</b> Набор 10 кг. Максимальный объем и вау-эффект."
    if qty == "0.5":
        return "🎁 <b>Описание:</b> Пробник 0.5 кг. Бесплатно за отзыв, количество ограничено."
    return "🌸 <b>Описание:</b> Свежие цветы с бесплатной доставкой по Паттайе."


@dp.message_handler(lambda message: message.text == f"/{ADMIN_PANEL_PASSWORD}")
async def admin_login(message: types.Message):
    grant_admin_access(message.from_user.id)
    await message.answer("✅ Доступ к админ-панели выдан. Используйте /admin")


@dp.message_handler(commands=['admin', 'adm', 'админ'])
async def admin_menu(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(f"👨‍⚖️ <b>Админ:</b> <code>{message.from_user.username}</code>", reply_markup=admin_but())
    else:
        await message.answer("⛔ Нет доступа. Введите пароль-команду.")


@dp.message_handler(lambda message: message.text == "💼 Профиль")
async def bot_send_user_profile(message: types.Message):
    photo = await bot.get_user_profile_photos(message.chat.id)
    cnt = photo.total_count
    if int(cnt) == 0:
        avatar = open('photos/cartel.jpg', 'rb')
    else:
        avatar = photo.photos[0][1]['file_id']

    await message.answer_photo(
        photo=avatar,
        caption=profile_text(message.chat.id, message.from_user.full_name),
        reply_markup=profile_but(message.chat.id),
    )


@dp.message_handler(lambda message: message.text == "💐 Заказать цветы")
async def bot_send_city(message: types.Message):
    with open("photos/cartel.jpg", "rb") as cartel:
        await message.answer_photo(photo=cartel, caption="🤵‍♂️ <code>Выберите цветы...</code>", reply_markup=staff_but())

    await MAKE_DEAL.staff.set()


@dp.message_handler(lambda message: message.text == "👨‍⚖️ Поддержка")
async def bot_send_support(message: types.Message):
    with open("photos/cartel.jpg", "rb") as cartel:
        await message.answer_photo(
            photo=cartel,
            caption="📑 <code>Мы на связи 24/7 для решения ваших вопросов.</code>",
            reply_markup=support_but(),
        )


@dp.message_handler(lambda message: message.text in staff_list, state=MAKE_DEAL.staff)
async def bot_send_rayon_info(message: types.Message, state=FSMContext):
    if "Пробник" in message.text:
        samples = get_samples()
        if samples <= 0:
            await message.answer("❌ <code>Пробники закончились. Выберите другой товар.</code>", reply_markup=staff_but())
            return

    async with state.proxy() as data:
        data['staff'] = message.text
        data['city'] = "💠 Паттайя"
        description = get_flower_description(message.text)

        with open("photos/cartel.jpg", "rb") as cartel:
            staff = message.text.split("—")[0]
            await message.answer_photo(
                photo=cartel,
                caption=(
                    f"<b>🌃 Город:</b> <code>Паттайя</code>\n"
                    f"📦 <b>Выбранные цветы:</b> <code>{staff[2:]}</code>\n\n"
                    f"{description}\n\n"
                    "🌆 <i>Напишите адрес доставки в Паттайе</i>\n"
                    "🤖 <i>Мы доставим цветы по указанному адресу бесплатно.</i>\n\n"
                    "📑 <b>Пример:</b> <code>Отель XYZ, комната 123.</code>\n\n"
                    "⚠️ <b>Укажите точный адрес для успешной доставки!</b>"
                ),
                reply_markup=buy_menu(),
            )

    await MAKE_DEAL.rayon.set()


@dp.message_handler(lambda message: message.text == "📂 Главное меню", state="*")
async def bot_back_menu(message: types.Message, state=FSMContext):
    await state.finish()
    with open("photos/cartel.jpg", "rb") as cartel:
        await message.answer_photo(photo=cartel, caption="📂 <code>Главное меню...</code>", reply_markup=main_menu())


@dp.message_handler(lambda message: message.text == "🌃 Вернутся к выбору города", state="*")
async def bot_back_city(message: types.Message, state=FSMContext):
    await state.finish()
    with open("photos/cartel.jpg", "rb") as cartel:
        await message.answer_photo(photo=cartel, caption="🤵‍♂️ <code>Выберите свой город...</code>", reply_markup=city_but())
    await MAKE_DEAL.city.set()


@dp.message_handler(state=MAKE_DEAL.rayon)
async def send_buy_info(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        city = data['city']
        staff_info = data['staff'].split("—")
        staff = staff_info[0]

        if "Пробник" in data['staff']:
            if not decrease_samples():
                await message.answer("❌ <code>Пробники закончились.</code>")
                await state.finish()
                return

        order_id = generate_id()
        amount_match = re.findall(r"\d+", data['staff'])
        amount = int(amount_match[-1]) if amount_match else 0
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        add_new_buy(message.chat.id, order_id, amount, staff[2:], city[2:], created_at)

        await state.finish()

        with open("photos/cartel.jpg", "rb") as cartel:
            await message.answer_photo(
                photo=cartel,
                caption=(
                    "✅ <code>Заказ оформлен!</code>\n\n"
                    f"🌃 <b>Город:</b> <code>{city[2:]}</code>\n"
                    f"📦 <b>Цветы:</b> <code>{staff[2:]}</code>\n"
                    f"🏠 <b>Адрес доставки:</b> <code>{message.text}</code>\n\n"
                    "🚚 <b>Доставка бесплатная по всему городу.</b>\n"
                    "📞 <b>Курьер свяжется с вами в ближайшее время.</b>"
                ),
                reply_markup=main_menu(),
            )

            try:
                await bot.send_message(
                    chat_id=LOGS_CHAT,
                    text=(
                        "🌸 Новый заказ цветов!\n"
                        f"Пользователь: <a href='tg://user?id={message.chat.id}'>{message.from_user.full_name}</a>\n"
                        f"└@{message.from_user.username}\n\n"
                        f"🌃 <b>Город:</b> <code>{city[2:]}</code>\n"
                        f"🏠 <b>Адрес:</b> <code>{message.text}</code>\n"
                        f"📦 <b>Цветы:</b> <code>{staff[2:]}</code>"
                    ),
                )
            except Exception as e:
                print(f"Error sending to LOGS_CHAT: {e}")


@dp.message_handler(state=SPAM_DATA.text)
async def get_text_for_spam(message: types.Message, state=FSMContext):
    await message.delete()
    async with state.proxy() as data:
        msg = await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data['message_id'],
            text="🖇 Введите данные для кнопки под текстом. Формат: текст ссылка. Если без кнопки — отправьте 0.",
            reply_markup=cancel_but(),
        )
        data['message_id'] = msg.message_id
        data['text'] = message.text
        await SPAM_DATA.but_info.set()


@dp.message_handler(state=SPAM_DATA.photo, content_types=ContentType.ANY)
async def get_photo_for_spam(message: types.Message, state=FSMContext):
    await message.delete()
    async with state.proxy() as data:
        if message.content_type == "photo":
            file_id = message.photo[0].file_id
            msg = await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=data['message_id'],
                text="💠 Введите текст под фото",
                reply_markup=cancel_but(),
            )
            data['photo'] = file_id
            data["message_id"] = msg.message_id
            await SPAM_DATA.caption.set()
        else:
            msg = await message.answer("Отправьте фото!")
            await asyncio.sleep(1)
            await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)


@dp.message_handler(state=SPAM_DATA.video, content_types=ContentType.ANY)
async def get_video_for_spam(message: types.Message, state=FSMContext):
    await message.delete()
    async with state.proxy() as data:
        if message.content_type == "video":
            file_id = message.video.file_id
            msg = await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=data['message_id'],
                text="💠 Введите текст под видео",
                reply_markup=cancel_but(),
            )
            data['video'] = file_id
            data["message_id"] = msg.message_id
            await SPAM_DATA.caption.set()
        else:
            msg = await message.answer("Отправьте видео!")
            await asyncio.sleep(1)
            await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)


@dp.message_handler(state=SPAM_DATA.animation, content_types=ContentType.ANY)
async def get_animation_for_spam(message: types.Message, state=FSMContext):
    await message.delete()
    async with state.proxy() as data:
        if message.content_type == "animation":
            file_id = message.animation.file_id
            msg = await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=data['message_id'],
                text="💠 Введите текст под гифку",
                reply_markup=cancel_but(),
            )
            data['animation'] = file_id
            data["message_id"] = msg.message_id
            await SPAM_DATA.caption.set()
        else:
            msg = await message.answer("Отправьте гифку!")
            await asyncio.sleep(1.5)
            await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)


@dp.message_handler(state=SPAM_DATA.caption)
async def get_caption(message: types.Message, state=FSMContext):
    await message.delete()
    async with state.proxy() as data:
        msg = await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data['message_id'],
            text="🖇 Введите данные для кнопки под текстом. Формат: текст ссылка. Если без кнопки — отправьте 0.",
            reply_markup=cancel_but(),
        )
        data['message_id'] = msg.message_id
        data['caption'] = message.text
        await SPAM_DATA.but_info.set()


@dp.message_handler(state=SPAM_DATA.but_info)
async def get_info_for_but(message: types.Message, state=FSMContext):
    await message.delete()
    async with state.proxy() as data:
        try:
            if "http" in message.text.split(" ")[1]:
                data['but_info'] = message.text
                key = spam_with_but(message.text.split(" ")[0], message.text.split(" ")[1])
        except Exception:
            data['but_info'] = 0
            key = spam_withot_but()

        if data["check_spam_type"] == "txt":
            await bot.delete_message(chat_id=message.chat.id, message_id=data['message_id'])
            msg = await message.answer(
                "Проверьте данные для рассылки.\n\n"
                f"{data['text']}\n\n"
                "Чтобы отправить рассылку отправьте + | чтобы отменить отправьте -",
                reply_markup=key,
            )
            data['message_id'] = msg.message_id
            await SPAM_DATA.confirm_spam.set()

        elif data["check_spam_type"] == "photo":
            await bot.delete_message(chat_id=message.chat.id, message_id=data['message_id'])
            msg = await message.answer_photo(
                photo=data['photo'],
                caption=(
                    "Проверьте данные для рассылки.\n"
                    "Чтобы отправить рассылку отправьте + | чтобы отменить отправьте -\n\n"
                    f"{data['caption']}"
                ),
                reply_markup=key,
            )
            data['message_id'] = msg.message_id
            await SPAM_DATA.confirm_spam.set()

        elif data["check_spam_type"] == "video":
            await bot.delete_message(chat_id=message.chat.id, message_id=data['message_id'])
            msg = await message.answer_video(
                video=data['video'],
                caption=(
                    "Проверьте данные для рассылки.\n"
                    "Чтобы отправить рассылку отправьте + | чтобы отменить отправьте -\n\n"
                    f"{data['caption']}"
                ),
                reply_markup=key,
            )
            data['message_id'] = msg.message_id
            await SPAM_DATA.confirm_spam.set()

        elif data["check_spam_type"] == "animation":
            await bot.delete_message(chat_id=message.chat.id, message_id=data['message_id'])
            msg = await message.answer_animation(
                animation=data['animation'],
                caption=(
                    "Проверьте данные для рассылки.\n"
                    "Чтобы отправить рассылку отправьте + | чтобы отменить отправьте -\n\n"
                    f"{data['caption']}"
                ),
                reply_markup=key,
            )
            data['message_id'] = msg.message_id
            await SPAM_DATA.confirm_spam.set()


@dp.message_handler(state=SPAM_DATA.confirm_spam)
async def get_confirm(message: types.Message, state=FSMContext):
    await message.delete()
    if "+" in message.text:
        async with state.proxy() as data:
            await bot.delete_message(chat_id=message.chat.id, message_id=data['message_id'])
            if data['but_info'] == 0:
                key = spam_withot_but()
            else:
                info = data['but_info'].split(" ")
                key = spam_with_but(info[0], info[1])

            if data["check_spam_type"] == "txt":
                text_for_spam = data['text']
                await state.finish()
                users = users_id_for_spam()
                k = 0
                l = 0
                msg = await message.answer("⚡️ Рассылка текстом успешно запущена.")
                for userid in users:
                    try:
                        await bot.send_message(chat_id=userid[0], text=text_for_spam, parse_mode="html", reply_markup=key)
                        k += 1
                        await asyncio.sleep(0.1)
                    except Exception as err:
                        l += 1
                        if "bot was blocked by the user" in str(err):
                            clear_bd(userid[0])
                        else:
                            logging.exception(err)

                await message.answer(
                    "✅ Рассылка текстом завершена.\n\n"
                    f"🔥 Доставлено: {k} сообщений\n"
                    f"💢 Не доставлено: {l} сообщений",
                    reply_markup=spam_withot_but(),
                )

            elif data["check_spam_type"] == "photo":
                file_id = data['photo']
                caption = data['caption']
                await state.finish()
                users = users_id_for_spam()
                k = 0
                l = 0
                msg = await message.answer("⚡️ Рассылка фото успешно запущена.")
                for userid in users:
                    try:
                        await bot.send_photo(chat_id=userid[0], photo=file_id, caption=caption, parse_mode="html", reply_markup=key)
                        k += 1
                        await asyncio.sleep(0.1)
                    except Exception as err:
                        l += 1
                        if "bot was blocked by the user" in str(err):
                            clear_bd(userid[0])
                        else:
                            logging.exception(err)

                await message.answer(
                    "✅ Рассылка фото завершена.\n\n"
                    f"🔥 Доставлено: {k} сообщений\n"
                    f"💢 Не доставлено: {l} сообщений",
                    reply_markup=spam_withot_but(),
                )

            elif data["check_spam_type"] == "video":
                file_id = data['video']
                await state.finish()
                users = users_id_for_spam()
                k = 0
                l = 0
                msg = await message.answer("⚡️ Рассылка видео успешно запущена.")
                for userid in users:
                    try:
                        await bot.send_video(chat_id=userid[0], video=file_id, parse_mode="html", reply_markup=key)
                        k += 1
                        await asyncio.sleep(0.1)
                    except Exception as err:
                        l += 1
                        if "bot was blocked by the user" in str(err):
                            clear_bd(userid[0])
                        else:
                            logging.exception(err)

                await message.answer(
                    "✅ Рассылка видео завершена.\n\n"
                    f"🔥 Доставлено: {k} сообщений\n"
                    f"💢 Не доставлено: {l} сообщений",
                    reply_markup=spam_withot_but(),
                )

            elif data["check_spam_type"] == "animation":
                file_id = data['animation']
                await state.finish()
                users = users_id_for_spam()
                k = 0
                l = 0
                msg = await message.answer("⚡️ Рассылка гифкой успешно запущена.")
                for userid in users:
                    try:
                        await bot.send_animation(chat_id=userid[0], animation=file_id, parse_mode="html", reply_markup=key)
                        k += 1
                        await asyncio.sleep(0.1)
                    except Exception as err:
                        l += 1
                        if "bot was blocked by the user" in str(err):
                            clear_bd(userid[0])
                        else:
                            logging.exception(err)

                await message.answer(
                    "✅ Рассылка гифкой завершена.\n\n"
                    f"🔥 Доставлено: {k} сообщений\n"
                    f"💢 Не доставлено: {l} сообщений",
                    reply_markup=spam_withot_but(),
                )

            await asyncio.sleep(5)
            await bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
    else:
        async with state.proxy() as data:
            await bot.delete_message(chat_id=message.chat.id, message_id=data['message_id'])
            await message.answer("⚡️ Рассылка успешно отменена.", reply_markup=admin_but())

        await state.finish()


@dp.message_handler(state=ADMIN_INFO.p2p)
async def bot_change_p2p(message: types.Message, state=FSMContext):
    await message.delete()
    p2p = message.text
    async with state.proxy() as data:
        if set_p2p(p2p):
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=data['message_id'],
                text="✅ <i>P2P ключ был успешно установлен.</i>",
                reply_markup=admin_but(),
            )
        else:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=data['message_id'],
                text="💢 <i>P2P ключ не установился.</i>",
                reply_markup=admin_but(),
            )

    await state.finish()


async def timer(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        info = all_buscket()
        if len(info) == 0:
            continue

        for i in info:
            info_staff = staff_info(i[0])
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            t1 = info_staff[7]
            t2 = str(now)
            date_format = "%Y-%m-%d %H:%M"
            t1_object = to_datetime_object(t1, date_format)
            t2_object = to_datetime_object(t2, date_format)
            check_time = str(t1_object - t2_object)
            if "day" in check_time or "days" in check_time:
                arr = check_time.split(" ")
                if int(arr[0]) <= 0:
                    delete_basket(info_staff[1])
            else:
                time_to_pay = check_time.split(":")[1]
                if time_to_pay in time_list:
                    await bot.send_message(
                        chat_id=info_staff[0],
                        text=f"🤵‍♂️ <code>Заказ #{info_staff[1]} | {info_staff[4]} осталось {time_to_pay} мин. на оплату...</code>",
                    )

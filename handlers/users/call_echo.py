import asyncio
import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types.input_media import InputMedia, InputFile

from bot_text import profile_text
from data.config import ADMINS, LOGS_CHAT
from keyboards.default.main_reply import main_menu
from keyboards.inline.main_admin import admin_but, spam_types, cancel_but
from keyboards.inline.main_inline import profile_but, support_but, busket_but, cancel_payment
from loader import dp, bot
from states.state import SPAM_DATA, ADMIN_INFO, BALANCE
from utils.admin_auth import has_admin_access
from utils.db_api.baza import get_user_buys, get_busket_info, count_users, admins_setting_info


def is_admin(user_id: int) -> bool:
    return has_admin_access(user_id) or str(user_id) in ADMINS


async def require_admin(call: types.CallbackQuery) -> bool:
    if is_admin(call.from_user.id):
        return True
    await call.answer('⛔ Нет доступа к админ-панели', show_alert=True)
    return False


@dp.callback_query_handler(text='accept_rules')
async def bot_send_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_caption('🌸 <code>Kitsune Shop</code>')
    await call.message.answer('⚡️', reply_markup=main_menu())


@dp.callback_query_handler(text='back_to_profile')
async def bot_back_to_profile(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_caption(
        profile_text(call.message.chat.id, call.from_user.full_name),
        reply_markup=profile_but(call.message.chat.id),
    )


@dp.callback_query_handler(text='my_buys')
async def bot_send_my_buys(call: types.CallbackQuery):
    buys = get_user_buys(call.message.chat.id)
    if not buys:
        await call.answer('☹️ У вас пока нет заказов')
        return

    lines = ['🛒 <b>Ваши заказы:</b>']
    for idx, buy in enumerate(buys[:10], start=1):
        staff_id, staff, city, summa, date = buy
        lines.append(
            f"{idx}. <b>{staff}</b> | {city} | {summa} бат\n"
            f"ID: <code>{staff_id}</code>\n"
            f"Дата: <code>{date}</code>"
        )

    await call.answer()
    await call.message.answer('\n\n'.join(lines))


@dp.callback_query_handler(text='close_spam')
async def bot_close_spam(call: types.CallbackQuery):
    try:
        await call.answer()
        await call.message.delete()
    except Exception:
        await call.answer('💢')


@dp.callback_query_handler(text='hide_adm')
async def bot_hide_admin(call: types.CallbackQuery):
    if not await require_admin(call):
        return
    await call.answer()
    await call.message.edit_text('🧛‍♀️ <code>Админ-панель скрыта...</code>')


@dp.callback_query_handler(text='check_pay')
async def bot_check_pay(call: types.CallbackQuery):
    await call.answer('💢 Платеж не найден')
    await bot.send_message(
        chat_id=LOGS_CHAT,
        text=(
            f'✅ Пользователь: <a href="tg://user?id={call.message.chat.id}">{call.from_user.full_name}</a>, '
            f'подтвердил оплату по реквизитам!\n└@{call.from_user.username}'
        ),
    )


@dp.callback_query_handler(text='back_to_admin')
async def back_to_admin(call: types.CallbackQuery):
    if not await require_admin(call):
        return
    await call.answer()
    await call.message.edit_text(
        f'👨‍⚖️ <b>Админ:</b> <code>{call.from_user.full_name}</code>',
        reply_markup=admin_but(),
    )


@dp.callback_query_handler(text='set_p2p')
async def bot_set_p2p(call: types.CallbackQuery, state=FSMContext):
    if not await require_admin(call):
        return
    await call.answer()
    msg = await call.message.edit_text('🔑 <b>Введите P2P ключ</b>', reply_markup=cancel_but())
    async with state.proxy() as data:
        data['message_id'] = msg.message_id
    await ADMIN_INFO.p2p.set()


@dp.callback_query_handler(text='stata')
async def statistik_info(call: types.CallbackQuery):
    if not await require_admin(call):
        return
    try:
        await call.message.edit_text(
            f'🤵‍♂️ На данный момент в боте {count_users()} чел.',
            reply_markup=admin_but(),
        )
    except Exception:
        await bot.answer_callback_query(call.id, 'Users info👇')


@dp.callback_query_handler(text='settings')
async def settings_info(call: types.CallbackQuery):
    if not await require_admin(call):
        return
    try:
        await call.message.edit_text(
            f'🔑 <b>P2P ключ:</b> <code>{admins_setting_info()[0]}</code>',
            reply_markup=admin_but(),
        )
    except Exception as err:
        logging.exception(err)
        await bot.answer_callback_query(call.id, 'Settings👇')


@dp.callback_query_handler(text='spam')
async def choose_types_spam(call: types.CallbackQuery):
    if not await require_admin(call):
        return
    await call.answer()
    await call.message.edit_text('✨ Выберите тип рассылки. Как будем отправлять?', reply_markup=spam_types())


@dp.callback_query_handler(text='spam_text')
async def send_text_for_spam(call: types.CallbackQuery, state=FSMContext):
    if not await require_admin(call):
        return
    await call.message.delete()
    await call.answer()
    msg = await call.message.answer('🌐 Введите текст для рассылки.', reply_markup=cancel_but())
    async with state.proxy() as data:
        data['message_id'] = msg.message_id
        data['check_spam_type'] = 'txt'
    await SPAM_DATA.text.set()


@dp.callback_query_handler(text='spam_pic')
async def send_pic_for_spam(call: types.CallbackQuery, state=FSMContext):
    if not await require_admin(call):
        return
    await call.message.delete()
    await call.answer()
    msg = await call.message.answer('🎆 Отправьте картинку для рассылки.', reply_markup=cancel_but())
    async with state.proxy() as data:
        data['message_id'] = msg.message_id
        data['check_spam_type'] = 'photo'
    await SPAM_DATA.photo.set()


@dp.callback_query_handler(text='spam_video')
async def send_video_for_spam(call: types.CallbackQuery, state=FSMContext):
    if not await require_admin(call):
        return
    await call.message.delete()
    await call.answer()
    msg = await call.message.answer('📹 Отправьте видео для рассылки.', reply_markup=cancel_but())
    async with state.proxy() as data:
        data['message_id'] = msg.message_id
        data['check_spam_type'] = 'video'
    await SPAM_DATA.video.set()


@dp.callback_query_handler(text='spam_gif')
async def send_gif_for_spam(call: types.CallbackQuery, state=FSMContext):
    if not await require_admin(call):
        return
    await call.message.delete()
    await call.answer()
    msg = await call.message.answer('🌄 Отправьте гифку для рассылки.', reply_markup=cancel_but())
    async with state.proxy() as data:
        data['message_id'] = msg.message_id
        data['check_spam_type'] = 'animation'
    await SPAM_DATA.animation.set()


@dp.callback_query_handler(text='basket')
async def basket_info(call: types.CallbackQuery):
    try:
        length = len(get_busket_info(call.message.chat.id))
        if length == 0:
            await call.answer('💢 Нет товара в корзине')
        else:
            await call.message.edit_caption(
                f'🗑 <b>Товаров в корзине:</b> <code>{length} шт.</code>',
                reply_markup=busket_but(get_busket_info(call.message.chat.id)),
            )
    except Exception:
        pass


@dp.callback_query_handler(text='cancel_payment', state='*')
async def bot_cancel_payment(call: types.CallbackQuery, state=FSMContext):
    await call.answer()
    photo = await bot.get_user_profile_photos(call.message.chat.id)
    cnt = photo.total_count
    if int(cnt) == 0:
        await call.message.edit_media(
            InputMedia(media=InputFile('photos/cartel.jpg'), caption=profile_text(call.message.chat.id, call.from_user.full_name)),
            reply_markup=profile_but(call.message.chat.id),
        )
    else:
        avatar = photo.photos[0][1]['file_id']
        await call.message.edit_media(
            InputMedia(media=avatar, caption=profile_text(call.message.chat.id, call.from_user.full_name)),
            reply_markup=profile_but(call.message.chat.id),
        )
    await state.finish()


@dp.callback_query_handler(text='add_qiwi')
async def payment_qiwi(call: types.CallbackQuery, state=FSMContext):
    await call.answer()
    msg = await call.message.edit_media(
        InputMedia(
            media=InputFile('photos/card_qiwi.png'),
            caption=(
                '💠 <b>Платежный метод пополнения:</b> <code>🥝 Qiwi |💳 Карта</code>\n\n'
                '♻️ <code>Введите сумму пополнения.</code>'
            ),
        ),
        reply_markup=cancel_payment(),
    )
    async with state.proxy() as data:
        data['message_id'] = msg.message_id
        await BALANCE.summa.set()


@dp.callback_query_handler(state='*')
async def call_answer(call: types.CallbackQuery, state=FSMContext):
    if call.data == 'cansel_spam':
        await call.answer()
        await call.message.edit_text('💢 <code>Действия отменено...</code>', reply_markup=admin_but())
        await state.finish()

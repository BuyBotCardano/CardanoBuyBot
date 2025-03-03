import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from cfg import TOKEN, BOT_USERNAME
from database import *
from functions import return_transactions, return_token_data
from messages import *


# keyboard btns

add_to_group_btn = types.InlineKeyboardMarkup().add(
    types.InlineKeyboardButton(url=f"http://t.me/{BOT_USERNAME}?startgroup", text="Add me to your group")
)


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class FSM(StatesGroup):
    chat_id = State()
    token_address = State()


@dp.message_handler(commands=['start'], state="*")
async def start_cmd_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await add_user(message.from_user.id)
    command_args = message.get_args()
    if not command_args:
        await message.reply(text=START_MSG, reply_markup=add_to_group_btn)
        return

    try:
        chat_info = await bot.get_chat(command_args)
        if chat_info and chat_info.type in ["group", "supergroup"]:
            admins = await bot.get_chat_administrators(chat_info.id)
            for admin in admins:
                if admin.user.id == message.from_user.id:
                    await state.update_data(chat_id=chat_info.id)
                    await message.reply(text=BACK_TO_BOT_MSG.format(chat_info.title),
                                        parse_mode="HTML")
                    await FSM.token_address.set()
                    return
            await message.reply(text=START_MSG, reply_markup=add_to_group_btn)
            return
    except Exception as e:
        await message.reply(text=START_MSG, reply_markup=add_to_group_btn)
        print(e)


@dp.message_handler(state=FSM.token_address)
async def sticker_pack_name_set_handler(message: types.Message, state: FSMContext):
    token_data = await return_token_data(message.text)
    print(token_data)
    if "ticker" not in token_data and token_data["error"]:
        await message.reply(text=INVALID_CONTRACT_MSG, parse_mode="HTML")
        return
    chat = await state.get_data()
    await state.finish()
    await add_token(token=message.text, group_id=chat.get("chat_id"), active=False, params=None)
    db_data = await get_chat_info(chat.get("chat_id"))

    btns = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(callback_data=f"toggle_df",
                                   text=f"Toggle [{'❌' if bool(db_data.get('active')) is False else '✅'}]"),

    ).add(types.InlineKeyboardButton(callback_data=f"_", text="⚙️ Settings")
          ).add(types.InlineKeyboardButton(callback_data=f"minbuy_{chat.get('chat_id')}", text="MIN BUY"),
                types.InlineKeyboardButton(callback_data=f"emoji_{chat.get('chat_id')}", text="EMOJI")).add(
        types.InlineKeyboardButton(callback_data=f"media_{chat.get('chat_id')}", text="MEDIA"),
        types.InlineKeyboardButton(callback_data=f"links_{chat.get('chat_id')}", text="LINKS")).add(
        types.InlineKeyboardButton(callback_data=f"preview_{chat.get('chat_id')}", text="BOT PREVIEW")
    )
    await message.reply(text=TOKEN_ADDED_MSG.format(token_data["ticker"]),
                        parse_mode="HTML",
                        reply_markup=btns)


@dp.callback_query_handler(lambda c: c.data == "toggle_df")
async def toggle_tx_detecting(callback_query: types.CallbackQuery):
    print("sws")
    group_id = callback_query.data.split("_")[-1]
    print(f"Group ID: {group_id}")
    await callback_query.answer(text="Status toggled!")


@dp.message_handler(content_types=['new_chat_members'])
async def send_welcome(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id

    for chat_member in message.new_chat_members:
        if chat_member.id == bot_id:
            back_to_bot_btn = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(url=f"http://t.me/{BOT_USERNAME}?start={message.chat.id}",
                                           text="Move to settings")
            )
            await message.reply(text=IN_GROUP_MSG, reply_markup=back_to_bot_btn)


async def new_tx_detector():
    while True:
        active_tokens = await get_active_tokens()
        if not active_tokens:
            print(active_tokens)
            await asyncio.sleep(5)
            continue
        await asyncio.sleep(5)


if __name__ == '__main__':
    create_db()
    loop = asyncio.get_event_loop()
    loop.create_task(new_tx_detector())
    executor.start_polling(dp)

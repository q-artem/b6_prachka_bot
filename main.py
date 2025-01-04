import asyncio
import logging
import sqlite3
from asyncio import sleep
from time import time

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
import re

from constants import hi_messages, default_lang
from db_utils import bd, get_value_from_id, enter_bd_request, write_value_from_id, add_user




logging.basicConfig(level=logging.INFO)  # Включаем логирование, чтобы не пропустить важные сообщения
dp = Dispatcher()  # Диспетчер
bot = Bot(token="7268025850:AAFvr8SgHLO929ESpSsPnaLlfwzjaEbn2fQ")


@dp.callback_query(F.data.startswith("send-hi-mess-on"))
async def sending_hi_mess(callback: types.CallbackQuery):
    _, lang = callback.data.split("_")
    await send_hi_mess(lang, callback.message)

    await callback.answer()


async def send_hi_mess(curr_lang: str, message: types.Message):
    kb = []

    for q in hi_messages.items():
        lang, to_lang = q[0], q[1]["to_lang"]
        if lang != curr_lang:
            kb.append([types.InlineKeyboardButton(text=to_lang, callback_data="send-hi-mess-on_" + lang)])

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=kb,
    )
    await message.answer(hi_messages[curr_lang]["mess"], reply_markup=keyboard)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if await get_value_from_id(message.from_user.id) is None:
        await add_user(message.from_user.id)
        await write_value_from_id(message.from_user.id, "isenable", 1)
        await message.answer("Запись создана. Приятного пользования!")
    else:
        await message.answer("Запись уже создана")
        # kb = [
        #     [
        #         types.InlineKeyboardButton(text="Отключить сообщения",
        #                                    callback_data="set-off_mess_" + str(message.from_user.id)),
        # ], [
        #         types.InlineKeyboardButton(text="Включить сообщения",
        #                                    callback_data="set-on_mess_" + str(message.from_user.id)),
        #     ]
        # ]
        # keyboard = types.InlineKeyboardMarkup(
        #     inline_keyboard=kb,
        # )
        # await message.answer("Кнопочки:", reply_markup=keyboard)
    await send_hi_mess(default_lang, message)


async def get_numbers(data: str) -> list[int]:
    _out = []
    for q in re.finditer(r"\d+", data):
        _out.append(int(q.string))
    cache = set(_out)
    out = []
    for q in _out:
        if q not in cache:
            out.append(q)
            cache.add(q)

    return out

async def main(bot_lc1):  # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot_lc1)
import asyncio
import logging
import sqlite3
from asyncio import sleep
from time import time

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.fsm.context import FSMContext

from db_utils import bd, get_value_from_id, enter_bd_request, write_value_from_id, add_user




logging.basicConfig(level=logging.INFO)  # Включаем логирование, чтобы не пропустить важные сообщения
dp = Dispatcher()  # Диспетчер
bot = Bot(token="7268025850:AAFvr8SgHLO929ESpSsPnaLlfwzjaEbn2fQ")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if await get_value_from_id(message.from_user.id) is None:
        for q in await get_value_from_id(0, get_all=True):
            user_id, enable, name = q
            if enable != 0:
                await bot.send_message(user_id, "ВНИМАНИЕ!!!!!\nКороче. Если вы это видите - не отправляйте фотки, кто-то посторонний подключился к боту, мне было лень делать защиту от этого. Позвоните Артёму, он починит.")
        await add_user(message.from_user.id)
        data = await write_value_from_id(message.from_user.id, "isenable", 1)
        await message.answer("Создание записи. Ответ БД: " + str(data))
        await message.answer("Введите имя (фото от ....):")
    else:
        await message.answer("Запись уже создана")
        kb = [
            [
                types.InlineKeyboardButton(text="Отключить сообщения",
                                           callback_data="set-off_mess_" + str(message.from_user.id)),
        ], [
                types.InlineKeyboardButton(text="Включить сообщения",
                                           callback_data="set-on_mess_" + str(message.from_user.id)),
            ]
        ]
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=kb,
        )
        await message.answer("Кнопочки:", reply_markup=keyboard)


async def main(bot_lc1):  # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot_lc1)
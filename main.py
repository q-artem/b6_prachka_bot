import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram import F
import re

from aiogram.types import ReplyKeyboardMarkup

from constants import *
from db_utils import get_value_from_id, enter_bd_request, write_value_from_id, add_user




logging.basicConfig(level=logging.INFO)  # Включаем логирование, чтобы не пропустить важные сообщения
dp = Dispatcher()  # Диспетчер
bot = Bot(token="7780365472:AAGed4EVuWqsNF0eDzusnuwc7mBRehqbrDg", default=DefaultBotProperties(parse_mode='html'))


@dp.callback_query(F.data.startswith("send-hi-mess-on"))
async def sending_hi_mess(callback: types.CallbackQuery):
    _, lang = callback.data.split("_")
    await send_hi_mess(lang, callback.message)

    await callback.answer()


async def send_hi_mess(curr_lang: str, message: types.Message):
    kb = []

    for q in T_hi_messages.items():
        lang, to_lang = q[0], q[1]["to_lang"]
        if lang != curr_lang:
            kb.append([types.InlineKeyboardButton(text=to_lang, callback_data="send-hi-mess-on_" + lang)])

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=kb,
    )
    await message.answer(T_hi_messages[curr_lang]["mess"], reply_markup=keyboard)


@dp.callback_query(F.data.startswith("select-language"))
async def select_language(callback: types.CallbackQuery):
    _, lang = callback.data.split("_")
    await write_value_from_id(callback.from_user.id, "language", lang)
    await callback.message.answer(T_selected_language[lang] + T_languages[lang])

    await send_hi_mess(lang, callback.message)
    await callback.answer()

@dp.callback_query(F.data.startswith("delete-all"))
async def delete_all(callback: types.CallbackQuery):
    _, curr_id = callback.data.split("_")
    lang = await get_value_from_id(curr_id, fields="language")

    await write_value_from_id(curr_id, "boxes", "")

    await bot.send_message(curr_id, T_success[lang])
    await send_current_queue(int(curr_id), [])
    await callback.answer()


@dp.callback_query(F.data.startswith("delete-last"))
async def delete_all(callback: types.CallbackQuery):
    _, curr_id = callback.data.split("_")
    lang = await get_value_from_id(curr_id, fields="language")

    boxes = list((await get_value_from_id(curr_id, fields="boxes")).split())
    if len(boxes) > 0:
        boxes = boxes[:-1]
        await write_value_from_id(curr_id, "boxes", " ".join(boxes))
        await bot.send_message(curr_id, T_success[lang])

    await send_current_queue(int(curr_id), boxes)
    await callback.answer()

@dp.callback_query(F.data.startswith("delete-box"))
async def delete_box(callback: types.CallbackQuery):
    _, curr_id, box = callback.data.split("_")
    lang = await get_value_from_id(curr_id, fields="language")
    boxes = list(map(int, (await get_value_from_id(curr_id, fields="boxes")).split()))
    if int(box) not in boxes:
        await bot.send_message(curr_id, T_box_are_not_exist[lang].format(box))
        await callback.answer()
        return
    boxes.pop(boxes.index(int(box)))
    await write_value_from_id(curr_id, "boxes", " ".join(list(map(str, boxes))))

    await bot.send_message(curr_id, T_success[lang])



async def send_current_queue(curr_id, queue, now_added=None):
    lang = await get_value_from_id(curr_id, fields="language")

    if len(queue) == 0:
        await bot.send_message(curr_id, T_queue_is_empty[lang])
    else:

        kb = [[types.InlineKeyboardButton(text=T_delete_all[lang],
                                          callback_data=f"delete-all_{curr_id}"),
               types.InlineKeyboardButton(text=T_delete_last[lang],
                                          callback_data=f"delete-last_{curr_id}")]
              ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

        if now_added is None:
            await bot.send_message(curr_id, T_now_tracking[lang].format(", ".join(map(str, queue))), reply_markup=keyboard)
        elif len(now_added) == 0:
            await bot.send_message(curr_id, T_error_added_to_tracking[lang].format(", ".join(map(str, queue))),reply_markup=keyboard)
        else:
            await bot.send_message(curr_id, T_added_to_tracking[lang].format(", ".join(map(str, now_added)), ", ".join(map(str, queue))),
                                   reply_markup=keyboard)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if await get_value_from_id(message.from_user.id) is None:
        await add_user(message.from_user.id)
        await write_value_from_id(message.from_user.id, "isenable", 1)
        await message.answer(" /\n".join(T_record_has_been_created.values()))
    else:
        await message.answer(" /\n".join(T_record_already_created.values()))
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
    kb = []

    for q in T_languages.items():
        key, value = q
        kb.append([types.InlineKeyboardButton(text=value, callback_data="select-language_" + key)])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await message.answer(" /\n".join(T_select_language.values()), reply_markup=keyboard)


@dp.message(F.text)
async def message_handler(message: types.Message):

    if message.chat.id == 1722948286:
        if message.text.split(" ")[0].lower() == "bd":
            dd = await enter_bd_request(" ".join(message.text.split(" ")[1:]))
            await message.answer(str(dd))
            return True
        if message.text.split(" ")[0].lower() == "users":
            data = await get_value_from_id(" ", get_all=True)
            lst = []
            for q in data:
                l = []
                for w in q:
                    l.append("<code>" + str(w) + "</code>")
                lst.append("("+", ".join(l) + ")")
            st = "["+ "\n".join(lst) + "]"
            await message.answer(st)
        if message.text.split(" ")[0].lower() == "stopbot":
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="да",
                                                             callback_data="stopbot")]],
            )
            await message.answer("Realno???", reply_markup=keyboard)
        spl = message.text.split(" ")
        if len(spl) > 2 and spl[0].lower() == "snd" and (spl[1].isdigit() or len(spl[1]) > 2 and spl[1][0] == "-" and spl[1][1:].isdigit()):
            idq = int(spl[1])
            try:
                await bot.send_message(idq, " ".join(spl[2:]))
            except TelegramBadRequest as e:
                await message.answer("Какая то ошибка: " + str(e))
                return True
            await message.answer("Готово!")
            return True

    numbers = await text_to_numbers(message.text)
    await write_numbers(message, numbers)


@dp.channel_post()
async def channel_message(message: types.MessageOriginChannel):
    # await bot.send_message(1722948286, )
    finding_boxes = await text_to_numbers(message.text)
    if_ready = True if "готов" in message.text else False
    for q in await get_value_from_id(0, get_all=True):
        curr_id, curr_lang, curr_boxes = q
        numbers = list(map(int, curr_boxes.split()))
        rewrite_bd = False
        for w in finding_boxes:
            if w in numbers:
                if if_ready:
                    await bot.send_message(curr_id, T_box_ready[curr_lang].format(w, link_to_channel + str(message.message_id)))
                    numbers.pop(numbers.index(w))
                    rewrite_bd = True
                else:
                    kb = [[types.InlineKeyboardButton(text=T_manually_delete_box[curr_lang].format(w), callback_data=f"delete-box_{curr_id}_{w}")]]
                    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

                    await bot.send_message(curr_id, T_box_maybe_ready[curr_lang].format(w, link_to_channel + str(message.message_id)), reply_markup=keyboard)
                    # await bot.forward_message(curr_id, message.chat.id, message.message_id)

        if rewrite_bd:
            await write_value_from_id(curr_id, "boxes", " ".join(list(map(str, numbers))))



async def get_numbers(message: types.Message):
    return list(map(int, (await get_value_from_id(message.from_user.id, fields="boxes")).split()))


async def write_numbers(message: types.Message, added_numbers):
    lang = await get_value_from_id(message.from_user.id, fields="language")
    numbers = await get_numbers(message) + added_numbers
    if len(numbers) > 100:
        await message.answer(T_too_many_boxes[lang])
        numbers = numbers[:100]
    out = []
    for q in numbers:
        if q not in out:
            out.append(q)
    out = list(map(str, out))

    await send_current_queue(message.from_user.id, out, added_numbers)
    await write_value_from_id(message.from_user.id, "boxes", " ".join(out))


async def text_to_numbers(data: str):
    _out = []
    for q in re.findall(r"\d+", data):
        _out.append(int(q))
    cache = set()
    out = []
    for q in _out:
        if q not in cache:
            out.append(q)
            cache.add(q)
    out1 = []
    for q in out:
        if q < 1000:
            out1.append(q)
    return out1

async def main(_bot):  # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(_bot)

asyncio.run(main(bot))
import asyncio
import logging
import os
from venv import logger

from transliterate import translit

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram import F
import re

from aiogram.types import FSInputFile

from constants import *
from db_utils import get_value_from_id, enter_bd_request, write_value_from_id, add_user
from mail import send_report_to_mail

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
dp = Dispatcher()
bot = Bot(token="1915599154:AAGHvs8tLqOY_gSIymWjzMjk0ooMeM2lbLk", default=DefaultBotProperties(parse_mode='html'))

all_media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documents')

file_ids: dict[int, list[(str, str)]] = dict()


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

    await callback.answer()


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
            await bot.send_message(curr_id, T_now_tracking[lang].format(", ".join(map(str, queue))),
                                   reply_markup=keyboard)
        elif len(now_added) == 0:
            await bot.send_message(curr_id, T_error_added_to_tracking[lang].format(", ".join(map(str, queue))),
                                   reply_markup=keyboard)
        else:
            await bot.send_message(curr_id, T_added_to_tracking[lang].format(", ".join(map(str, now_added)),
                                                                             ", ".join(map(str, queue))),
                                   reply_markup=keyboard)


@dp.callback_query(F.data.startswith("stopbot"))
async def set_age(callback: types.CallbackQuery):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await callback.message.answer("Окок")

    await callback.answer()

    exit()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if await get_value_from_id(message.from_user.id) is None:
        await add_user(message.from_user.id)
        await write_value_from_id(message.from_user.id, "isenable", 1)
        await message.answer(" /\n".join(T_record_has_been_created.values()))
        await bot.send_message(1722948286, "Добавлен: " + message.from_user.first_name + (
            (" " + message.from_user.last_name + ", @") if not message.from_user.last_name is None else ", @") + str(
            message.from_user.username) + " (id: <code>" + str(message.from_user.id) + "</code>)")
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


@dp.message(F.document)
async def document_handler(message: types.Message):
    lang = await get_value_from_id(message.from_user.id, fields="language")
    if (("." not in message.document.file_name) or message.document.file_name.split(".")[-1].lower()
            not in ["pdf", "doc", "docx", "jpg", "jpeg", "png", "xls", "xlsx", "csv", "ppt", "txt", "rtf", "tiff"]):
        await incorrect_data_handler(message)
        return False
    if message.document.file_size > 1024 * 1024 * 5:
        await message.answer(T_exceeding_file_size[lang])
        return False

    file_name = translit(message.document.file_name, 'ru',
                         reversed=True).encode('ascii', errors='ignore').decode().replace(" ", "_")

    if message.from_user.id not in file_ids.keys():
        file_ids[message.from_user.id] = []

    error_adding_file = False
    if len(file_ids[message.from_user.id]) < 10:
        file_ids[message.from_user.id].append((file_name, message.document.file_id))
        logger.info("Added file: " + message.document.file_id + ", User: " + str(message.from_user.id))
    else:
        error_adding_file = True
        logger.info("Error adding file: " + message.document.file_id + ", User: " + str(message.from_user.id))

    await send_message_about_added_file(message.from_user.id, error_adding_file=error_adding_file)


@dp.message(F.photo)
async def photo_handler(message: types.Message):
    print(message.photo)
    await message.answer("12")

    file = await bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path
    print(file_path)
    photo_name = translit(message.photo[-1].file_id + ".jpg", 'ru',
                          reversed=True).encode('ascii', errors='ignore').decode().replace(" ", "_")

    await bot.download_file(file_path, os.path.join(all_media_dir, photo_name))
    await message.reply_document(document=FSInputFile(path=os.path.join(all_media_dir, photo_name)))
    await send_report_to_mail([], os.path.join(all_media_dir, photo_name), photo_name)
    os.remove(os.path.join(all_media_dir, photo_name))


async def send_message_about_added_file(user_id: int, error_adding_file: bool = False,
                                        deleted_file_on_number: bool = False, file_number: int = 0):
    lang = await get_value_from_id(user_id, fields="language")

    msg = ""
    if error_adding_file:
        msg += T_cant_add_more_files[lang]
    elif deleted_file_on_number:
        msg += T_file_with_number_has_been_deleted[lang].format(file_number)
    else:
        msg += T_added_new_file[lang]
    msg += "\n\n" + T_current_list_to_send[lang]
    msg += "\n" + T_boxes[lang] + " "
    boxes = (await get_value_from_id(user_id, fields="boxes")).split()  # список
    if not boxes:
        msg += f"<i>{T_no_tracking_boxes[lang]}</i>\n"
    else:
        msg += " ".join(boxes) + "\n"
    msg += T_files[lang] + "\n"
    for q in range(len(file_ids[user_id])):
        msg += str(q + 1) + ") " + file_ids[user_id][q][0] + "\n"

    msg += "\n<i>" + T_to_send_or_delete[lang] + "</i>"

    col_files = len(file_ids[user_id])

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text=T_send[lang],
                                                     callback_data="send-letter"),
                          types.InlineKeyboardButton(text=T_delete_all_files[lang],
                                                     callback_data="delete-files-all")],
                         [types.InlineKeyboardButton(
                             text=((T_delete_file[lang] + " ") if col_files < 3 else "") + str(q + 1),
                             callback_data="delete-file-on-number_" + str(q + 1)) for q in range(0, min(5, col_files))],
                         [types.InlineKeyboardButton(
                             text=((T_delete_file[lang] + " ") if col_files - 5 < 3 else "") + str(q + 1),
                             callback_data="delete-file-on-number_" + str(q + 1)) for q in range(5, min(10, col_files))]
                         ],
    )

    await bot.send_message(user_id, msg, reply_markup=keyboard)


@dp.callback_query(F.data.startswith("send-letter"))
async def send_letter(callback: types.CallbackQuery):
    lang = await get_value_from_id(callback.from_user.id, fields="language")

    boxes = (await get_value_from_id(callback.from_user.id, fields="boxes")).split()
    files = file_ids[callback.from_user.id].copy()
    if len(files) == 0:
        await callback.message.answer(T_no_files_to_send[lang])
        await callback.answer()
        return False
    if len(boxes) == 0:
        await callback.message.reply(T_no_boxes_to_send[lang])
        await callback.answer()
        return False

    file_ids[callback.from_user.id] = []

    status = await callback.message.answer(T_preparing_to_send[lang])

    file_patches = []
    for q in files:
        file = await bot.get_file(q[1])
        file_path = file.file_path
        file_patches.append((file_path, q[1]))

    await status.edit_text(T_downloading_files[lang])

    for q in file_patches:
        await bot.download_file(q[0], os.path.join(all_media_dir, q[1]))

    await status.edit_text(T_building_letter[lang])

    file_patches_to_send = []
    for q in file_patches:
        file_patches_to_send.append(os.path.join(all_media_dir, q[1]))
    file_names_to_send = []
    for q in files:
        file_names_to_send.append(q[0])

    try:
        await send_report_to_mail(boxes, file_patches_to_send, file_names_to_send, status, lang, callback.from_user)
    except Exception as e:
        await callback.message.answer(T_error_on_sending[lang])
        await callback.answer()
        logger.error(e)
        return False

    await status.edit_text(T_letter_has_been_sent[lang])

    for q in file_patches_to_send:
        os.remove(q)

    await callback.answer()


@dp.callback_query(F.data.startswith("delete-file-on-number"))
async def delete_file_on_number(callback: types.CallbackQuery):
    lang = await get_value_from_id(callback.from_user.id, fields="language")
    file_number = int(callback.data.split("_")[1])
    if (callback.from_user.id not in file_ids.keys()) or (len(file_ids[callback.from_user.id]) < file_number):
        await callback.answer(T_list_not_contains_this_number[lang].format(file_number), show_alert=True)
        return False
    file_ids[callback.from_user.id].pop(file_number - 1)
    if len(file_ids[callback.from_user.id]) == 0:
        await delete_all_files(callback)
    else:
        await send_message_about_added_file(callback.from_user.id, deleted_file_on_number=True, file_number=file_number)
    await callback.answer()


@dp.callback_query(F.data.startswith("delete-files-all"))
async def delete_all_files(callback: types.CallbackQuery):
    lang = await get_value_from_id(callback.from_user.id, fields="language")
    file_ids[callback.from_user.id] = []
    await callback.message.answer(T_all_files_have_been_deleted[lang])
    await callback.answer()


@dp.message(F.video | F.audio | F.animation | F.location | F.sticker | F.contact | F.poll | F.voice)
async def incorrect_data_handler(message: types.Message):
    lang = await get_value_from_id(message.from_user.id, fields="language")
    await message.answer(T_incorrect_data[lang])


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
                lst.append("(" + ", ".join(l) + ")")
            st = "[" + "\n".join(lst) + "]"
            await message.answer(st)
        if message.text.split(" ")[0].lower() == "stopbot":
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="да",
                                                             callback_data="stopbot")]],
            )
            await message.answer("Realno???", reply_markup=keyboard)
        if message.text.lower() == "бд на базу":
            await message.answer_document(document=types.input_file.FSInputFile("users.sqlite"))
            return True
        spl = message.text.split(" ")
        if len(spl) > 2 and spl[0].lower() == "snd" and (
                spl[1].isdigit() or len(spl[1]) > 2 and spl[1][0] == "-" and spl[1][1:].isdigit()):
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
                    await bot.send_message(curr_id,
                                           T_box_ready[curr_lang].format(w, link_to_channel + str(message.message_id)))
                    numbers.pop(numbers.index(w))
                    rewrite_bd = True
                else:
                    kb = [[types.InlineKeyboardButton(text=T_manually_delete_box[curr_lang].format(w),
                                                      callback_data=f"delete-box_{curr_id}_{w}")]]
                    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

                    await bot.send_message(curr_id, T_box_maybe_ready[curr_lang].format(w, link_to_channel + str(
                        message.message_id)), reply_markup=keyboard)
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


def start_bot():
    if os.listdir("documents"):
        logger.info("Deleting old files...")
        for q in os.listdir("documents"):
            os.remove(os.path.join(all_media_dir, q))
        logger.info("All old files deleted")

    asyncio.run(main(bot))


start_bot()

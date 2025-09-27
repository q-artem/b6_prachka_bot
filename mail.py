from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from aiofiles import open as aopen
import aiosmtplib

from aiogram import types
from aiogram.client.session.middlewares.request_logging import logger

from constants import T_login_to_server, T_sending_letter
from datetime import datetime, timezone, timedelta

from constants import DEBUG


async def send_report_to_mail(boxes: list[str], file_patches: list[str], file_names: list[str], status: types.Message,
                              lang: str, user: types.User):
    from_email = "b6prachkabot@mail.ru"
    to_email = "prachka06@bk.ru"
    if DEBUG:
        to_email = "Stodvalista.genshin@mail.ru"
    smtp_server = "smtp.mail.ru"
    port = 465
    username = "b6prachkabot@mail.ru"
    password = "8Qvr7NwpluJc2vxuA1hd"

    time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=3)))
    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = from_email, to_email, "Чек " + time.strftime(
        "%H:%M:%S") + "    Боксы: " + ", ".join(boxes[:10]) + ("..." if len(boxes) > 10 else "")
    text = ""
    hour = time.hour
    if 5 <= hour < 12:
        text += "Доброе утро!"
    elif 12 <= hour < 17:
        text += "Добрый день!"
    elif 17 <= hour < 23:
        text += "Добрый вечер!"
    else:
        text += "Доброй ночи!"
    text += "<br>Это автоматически сформированное письмо. <br><u><b>Не отвечайте на него</b></u>, если нужно сообщить студенту о чем-либо, напишите о его боксе в чате прачечной, например \"бокс 54 нет чека\", и ему придет уведомление.<br><br>Имя пользователя в telegram: "
    text += user.first_name + ((" " + user.last_name) if not user.last_name is None else "") + "<br>"
    if not user.username is None:
        text += "Ссылка на профиль в telegram: https://t.me/" + user.username + "<br>"
    text += "ID пользователя: " + str(user.id) + "<br>"
    text += "Список боксов: " + ", ".join(boxes) + "<br>"
    text += "Время и дата отправки: " + time.strftime("%d.%m.%Y %H:%M:%S") + "<br><br><br>"
    text += "По вопросам работы бота обращайтесь к <a href='https://t.me/j_artem'>@j_artem</a> в telegram."
    msg.attach(MIMEText(text, 'html'))

    for file_path, file_name in zip(file_patches, file_names):
        async with aopen(file_path, "rb") as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(await file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={file_name}")

        msg.attach(part)

    await status.edit_text(T_login_to_server[lang])

    smtp_client = aiosmtplib.SMTP(
        hostname=smtp_server,
        port=port,
        use_tls=True,
        timeout=5
    )

    await smtp_client.connect()

    log = await smtp_client.login(username, password)
    logger.info(log)

    await status.edit_text(T_sending_letter[lang])

    log = await smtp_client.send_message(msg)
    logger.info(log)

    smtp_client.close()

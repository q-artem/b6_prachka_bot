import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from os import remove
import time

from aiogram import types


async def send_report_to_mail(boxes: list[int], file_path: str, file_name: str):

    from_email = "b6prachkabot@mail.ru"
    to_email = "Stodvalista.genshin@mail.ru"
    smtp_server = "smtp.mail.ru"
    port = 465
    username = "b6prachkabot@mail.ru"
    password = "8Qvr7NwpluJc2vxuA1hd"

    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = from_email, to_email, str(time.strftime("%Y-%m-%d %H:%M:%S"))
    msg.attach(MIMEText("Содержимое письма", 'plain'))

    for q in range(10):

        with open(file_path, "rb") as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={file_name}")

        msg.attach(part)

    server = smtplib.SMTP_SSL(smtp_server, port, timeout=10)
    print(server.login(username, password))
    print(server.send_message(msg))
    server.quit()


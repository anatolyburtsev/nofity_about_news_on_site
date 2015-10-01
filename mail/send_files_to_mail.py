# -*- coding: utf-8
import os
import time
from smtplib import SMTP
import email
from email import MIMEMultipart
from email import MIMEText
from email import MIMEBase
from email import Encoders
import config
import random


def choose_random_file_from_dir_on_hdd(path_to_dir):
    files = os.listdir(path_to_dir)
    return os.path.join(path_to_dir, files[random.randrange(len(files))])


def send_files_to_email(fromaddr=config.email_from_addr,
                        toaddr=config.email_to_addr,
                        frompassword=config.email_from_password,
                        path_to_dir=config.gif_dir_random,
                        count_of_files=10,
                        delele_files=False):
    attachment_size = 0
    # создаем почтовое сообщение
    msg = MIMEMultipart.MIMEMultipart()
    # заполняем поля отправителя, адресата и тему сообщения
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'gifs '+time.asctime()

    # текстовая часть сообщения (не забываем указать кодировку)
    msg.attach(MIMEText.MIMEText("свежая порция гифочек", "plain", "utf-8"))

    for i in range(count_of_files):
        file_to_send = choose_random_file_from_dir_on_hdd(path_to_dir)
        attachment_size += os.stat(file_to_send).st_size
        if attachment_size > 1.05 * config.email_limit:
            break
        # прикрепляем файл backup.tar.gz к почтовому сообщению
        att = MIMEBase.MIMEBase('application', 'octet-stream')
        att.set_payload(open(file_to_send, "rb").read())
        Encoders.encode_base64(att)
        att.add_header('Content-Disposition', 'attachment; filename="' + file_to_send +'"')
        msg.attach(att)

    # соединяемся с почтовым сервером и выполняем авторизацию
    server = SMTP('smtp.mail.ru', 25)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(fromaddr, frompassword)

    # отправляем сформированное сообщение, после чего выходим
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_files_to_email()
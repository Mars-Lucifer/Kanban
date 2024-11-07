import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

def send_mail_ru_email(recipient_email, subject, html_content):
    """Отправляет письмо по корпоративной почте mail.ru в формате HTML.

    Args:
        recipient_email (str): Адрес получателя.
        subject (str): Тема письма.
        html_content (str): HTML-содержимое письма.

    Returns:
        None
    """

    # Настройки корпоративной почты mail.ru
    sender_email = 'hello@irminsul.space'  
    sender_password = os.getenv('EMAIL_PASSWORD')  # Загружаем пароль из .env

    if not sender_password:
        raise ValueError("Пароль не найден в переменной окружения.")

    # Создание сообщения
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Добавление HTML-содержимого
    msg.attach(MIMEText(html_content, 'html'))

    # Отправка письма
    with smtplib.SMTP_SSL('smtp.mail.ru', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

# HTML-контент с нужным текстом
html_content = """
<html>
<head>
  <title>Пример письма от Mail.ru</title>
</head>
<body>
  <h1>Внимание!</h1>
  <p>Это письмо отправлено с корпоративной почты Mail.ru.</p>
</body>
</html>
"""

send_mail_ru_email('nikitarybalko897@gmail.com', 'Message', html_content)
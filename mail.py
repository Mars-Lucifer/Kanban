import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_vk(subject, body, to_email, from_email, from_password, smtp_server='smtp.mail.ru', smtp_port=587):
    try:
        # Создаем объект сообщения
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Добавляем тело письма
        msg.attach(MIMEText(body, 'plain'))

        # Подключаемся к SMTP серверу и отправляем письмо
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Включаем защищенное соединение
            server.login(from_email, from_password)  # Логинимся на почтовом сервере
            server.sendmail(from_email, to_email, msg.as_string())  # Отправляем письмо

        print("Письмо отправлено успешно!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")

send_email_vk(
    subject="Тема письма",
    body="Текст письма",
    to_email="nikitarybalko897@gmail.com",
    from_email="hello@irminsil.space",  # Почта ВКонтакте
    from_password="LNpR5sEsgvYVdUSPk2pp"  # Пароль от почты
)

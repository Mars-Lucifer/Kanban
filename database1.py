from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets
import smtplib
import string
import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kanban'
}


def readFromDb(db, table, record_id):
    connection = pymysql.connect(**db)

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM `{table}` WHERE `id` =%s", (record_id,))
        record = cursor.fetchone()

        if record is not None:
            # Получаем имена столбцов
            columns = [col[0] for col in cursor.description]
            # Преобразуем кортеж в словарь
            record_dict = dict(zip(columns, record))
            return record_dict


def getAllRecords(db, table):
    connection = pymysql.connect(**db)

    with connection.cursor() as cursor:
        sql =f"SELECT * FROM `{table}`"
        cursor.execute(sql)
        records=cursor.fetchall()
        return records if records is not None else "Записей нету"

def writeToDb(db, table, params, record):
    """
    Функция для добавления записи в базу данных.

    :param db: Конфигурация базы данных.
    :param table: Название таблицы.
    :param params: Список колонок таблицы.
    :param record: Кортеж значений для вставки.
    :return: ID последней добавленной записи или сообщение об ошибке.
    """
    try:
        connection = pymysql.connect(**db)
        with connection.cursor() as cursor:
            # Генерация SQL-запроса
            columns = ", ".join(f"`{param}`" for param in params)
            placeholders = ", ".join(["%s"] * len(params))
            sql = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"

            # Отладочная информация
            print(f"SQL-запрос: {sql}")
            print(f"Значения: {record}")

            # Выполнение запроса
            cursor.execute(sql, record)
            connection.commit()

            # Возврат ID последней записи
            last_id = cursor.lastrowid
            return last_id
    except pymysql.MySQLError as e:
        print(f"Ошибка при добавлении записи: {e}")
        return None
    finally:
        connection.close()
    

def addUser(user_id, name, surname, patronymic, email, password):
    new_user = (
        user_id,
        name,
        surname,
        patronymic,
        email,
        password,
        1
    )
    params =[
        "id",
        "name",
        "surname",
        "patronymic",
        "email",
        "password",
        "verification"
    ]
    writeToDb(DB_CONFIG,'users', params, new_user)

def addResume(photo_url, name, surname, patronymic, position, salary, experience, dateBirth, telephone, email, tag, education, comment, hr_fio, creation_date):
    new_resume = (
        photo_url,
        name,
        surname,
        patronymic,
        position,
        salary,
        experience,
        dateBirth,
        telephone,
        email,
        tag,
        education,
        comment,
        1,  # Допустим, это значение фиксировано (например, статус резюме)
        hr_fio,
        creation_date,
    )
    writeToDb('resumes', new_resume)

def addResume(photo_url, name, surname, patronymic, position, salary, experience, dateBirth, telephone, email, education, comment, hr_fio, creation_date):
    table_name = "resumes"
    params = [
        "photo", "name", "surname", "patronymic", "position", "salary", "experience", 
        "dateBirth", "telephone", "email", "education", "comment", "glass",
        "hr_fio", "creation_date"
    ]
    record = [
        photo_url, name, surname, patronymic, position, salary, experience, 
        dateBirth, telephone, email, education, comment, 1, hr_fio, creation_date
    ]
    
    return writeToDb(DB_CONFIG, table_name, params, record)

def updateInDb(db, table, record_id, updates):
    connection = pymysql.connect(**db)

    try:
        with connection.cursor() as cursor:
            # Используем параметризованный запрос для безопасности
            cursor.execute(f"UPDATE `{table}` SET `glass`=%s WHERE `id`=%s", (updates, record_id))
        
        connection.commit()  # Не забывайте сохранять изменения в базе данных

    except Exception as e:
        print(f"Ошибка при обновлении записи: {e}")
        connection.rollback()  # Откатываем транзакцию в случае ошибки

    finally:
        connection.close()



def updateFileInDb(db, resume_id, file_num, file_path):
    connection = pymysql.connect(**db)

    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO `files`(resume_id, file_url) VALUES (%s,%s)", (resume_id, file_path,))
        connection.commit()
        
# def updateInDb(table, record_id, updates):
#     with open(db_filename, 'r', encoding='utf-8') as db_file:
#         data = json.load(db_file)
    
#     for record in data.get(table, []):
#         if record.get('id') == record_id:
#             record.update(updates)
#             with open(db_filename, 'w', encoding='utf-8') as db_file:
#                 json.dump(data, db_file, indent=4)
#             logAction("updateInDb", f"Updated record with ID {record_id} in table '{table}': {updates}")
#             return True  # Успешное обновление
#     logAction("updateInDb", f"Record with ID {record_id} not found in table '{table}'")
#     return False  # Запись не найдена





# def updateFileInDb(db, resume_id, file_num, file_path):
#     connection = pymysql.connect(**db)

    # with open(db_filename, 'r') as db_file:
    #     data = json.load(db_file)

    # # Находим нужное резюме по ID
    # for record in data.get('resumes', []):
    #     if record.get('id') == resume_id:
    #         # Проверяем, что file_num валидный (от 1 до 3)
    #         if 1 <= file_num <= 3:
    #             # Обновляем нужное поле в массиве files
    #             record['files'][file_num - 1] = [1, file_path]
                
    #             # Сохраняем изменения в базе данных
    #             with open(db_filename, 'w') as db_file:
    #                 json.dump(data, db_file, indent=4)

    #             logAction("updateFileInDb", f"Updated file {file_num} for resume {resume_id}: {file_path}")
    #             return True
    #         else:
    #             logAction("updateFileInDb", f"Invalid file number {file_num} for resume {resume_id}")
    #             return False
    # logAction("updateFileInDb", f"Resume with ID {resume_id} not found.")
    # return False


def generate_activation_code(length=6):
    characters = string.ascii_letters + string.digits  # Буквы и цифры
    code = ''.join(secrets.choice(characters) for i in range(length))
    return code




# s= smtplib.SMTP("smtp.gmail.com", 587)
# s.starttls()
# s.login("kitp9615@gmail.com", "sckg nmrd nhcn efru")
# message="message"
# s.sendmail("kitp9615@gmail.com", "lebronstreed@gmail.com", message)
# s.quit()
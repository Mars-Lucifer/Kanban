import json
import os
from datetime import datetime

# Файлы базы данных и логов
db_filename = 'database.json'
log_filename = 'log.txt'

# Проверка наличия файла и создание, если его нет
def initDb():
    if not os.path.exists(db_filename):
        data = {
            "users": [],
            "resumes": []
        }
        with open(db_filename, 'w') as db_file:
            json.dump(data, db_file, indent=4)
        logAction("initDb", "Database initialized with empty tables.")
    else:
        print("База данных существует!")


# Функция логирования действий
def logAction(action, details):
    with open(log_filename, 'a') as log_file:
        log_entry = f"{datetime.now()} | Action: {action} | Details: {details}\n"
        log_file.write(log_entry)


# Чтение из базы данных по ID (пользователь или резюме)
def readFromDb(table, record_id):
    with open(db_filename, 'r') as db_file:
        data = json.load(db_file)
    
    for record in data.get(table, []):
        if record.get('id') == record_id:
            logAction("readFromDb", f"Read record with ID {record_id} from table '{table}'")
            return record
    logAction("readFromDb", f"Record with ID {record_id} not found in table '{table}'")
    return None

# Новая функция для получения всех записей из таблицы
def getAllRecords(table):
    with open(db_filename, 'r') as db_file:
        data = json.load(db_file)
    logAction("getAllRecords", f"Retrieved all records from table '{table}'")
    return data.get(table, [])


# Запись новой записи в таблицу
def writeToDb(table, record):
    with open(db_filename, 'r') as db_file:
        data = json.load(db_file)
    
    data.get(table, []).append(record)
    
    with open(db_filename, 'w') as db_file:
        json.dump(data, db_file, indent=4)
    
    logAction("writeToDb", f"Added record to table '{table}': {record}")


# Функция для изменения объекта в базе данных
def updateInDb(table, record_id, updates):
    with open(db_filename, 'r') as db_file:
        data = json.load(db_file)
    
    for record in data.get(table, []):
        if record.get('id') == record_id:
            record.update(updates)
            with open(db_filename, 'w') as db_file:
                json.dump(data, db_file, indent=4)
            logAction("updateInDb", f"Updated record with ID {record_id} in table '{table}': {updates}")
            return True  # Успешное обновление
    logAction("updateInDb", f"Record with ID {record_id} not found in table '{table}'")
    return False  # Запись не найдена


# Пример функций добавления с фиксированными полями
def addUser(user_id, name, surname, patronymic, email, password):
    new_user = {
        "id": user_id,
        "name": name,
        "surname": surname,
        "patronymic": patronymic,
        "email": email,
        "password": password,
        "verification": 1
    }
    writeToDb('users', new_user)

def addResume(resume_id, photo_url, name, surname, patronymic, post, salary, experience, dateBirth, telephone, email, tag, education, comment, hr_fio, creation_date):
    new_resume = {
        "id": resume_id,
        "photo": photo_url,
        "name": name,
        "surname": surname,
        "patronymic": patronymic,
        "post": post,
        "salary": salary,
        "experience": experience,
        "dateBirth": dateBirth,
        "telephone": telephone,
        "email": email,
        "tag": tag,
        "education": education,
        "comment": comment,
        "glass": 1,
        "hr_fio": hr_fio,
        "creation_date": creation_date,
        "files": [
            [0, ''],  # Скрининг (не прикреплен)
            [0, ''],  # Результат собеседования (не прикреплен)
            [0, '']   # Оффер (не прикреплен)
        ]
    }
    writeToDb('resumes', new_resume)


def updateFileInDb(resume_id, file_num, file_path):
    # Получаем все резюме
    with open(db_filename, 'r') as db_file:
        data = json.load(db_file)

    # Находим нужное резюме по ID
    for record in data.get('resumes', []):
        if record.get('id') == resume_id:
            # Проверяем, что file_num валидный (от 1 до 3)
            if 1 <= file_num <= 3:
                # Обновляем нужное поле в массиве files
                record['files'][file_num - 1] = [1, file_path]
                
                # Сохраняем изменения в базе данных
                with open(db_filename, 'w') as db_file:
                    json.dump(data, db_file, indent=4)

                logAction("updateFileInDb", f"Updated file {file_num} for resume {resume_id}: {file_path}")
                return True
            else:
                logAction("updateFileInDb", f"Invalid file number {file_num} for resume {resume_id}")
                return False
    logAction("updateFileInDb", f"Resume with ID {resume_id} not found.")
    return False

def deleteFromDb(table, record_id):
    with open(db_filename, 'r') as db_file:
        data = json.load(db_file)
    
    table_data = data.get(table, [])
    new_table_data = [record for record in table_data if record.get('id') != record_id]
    
    if len(new_table_data) == len(table_data):
        logAction("deleteFromDb", f"Record with ID {record_id} not found in table '{table}'")
        return False  # Запись не найдена
    
    data[table] = new_table_data
    with open(db_filename, 'w') as db_file:
        json.dump(data, db_file, indent=4)
    
    logAction("deleteFromDb", f"Deleted record with ID {record_id} from table '{table}'")
    return True

import json
import os

# Файл базы данных
db_filename = 'database.json'

# Проверка наличия файла и создание, если его нет
def init_db():
    if not os.path.exists(db_filename):
        data = {
            "users": [],  # Таблица пользователей
            "resumes": []  # Таблица резюме
        }
        with open(db_filename, 'w') as db_file:
            json.dump(data, db_file, indent=4)
    else:
        print("База данных существует!")

# Чтение из базы данных по ID (пользователь или резюме)
def read_from_db(table, record_id):
    with open(db_filename, 'r') as db_file:
        data = json.load(db_file)
    
    for record in data.get(table, []):
        if record.get('id') == record_id:
            return record
    return None  # Если запись не найдена

# Запись новой записи в таблицу
def write_to_db(table, record):
    with open(db_filename, 'r') as db_file:
        data = json.load(db_file)
    
    data.get(table, []).append(record)
    
    with open(db_filename, 'w') as db_file:
        json.dump(data, db_file, indent=4)

# Функции для добавления новых записей
def add_user(user_id, name, email):
    new_user = {
        "id": user_id,
        "name": name,
        "email": email
    }
    write_to_db('users', new_user)

def add_resume(resume_id, user_id, job_title, skills):
    new_resume = {
        "id": resume_id,
        "user_id": user_id,
        "job_title": job_title,
        "skills": skills
    }
    write_to_db('resumes', new_resume)

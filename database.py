import hashlib
import json
import os
import secrets
import string
import time
import pymysql
from datetime import datetime
import pytz

# Файлы базы данных и логов
db_filename = 'database.json'
log_filename = 'log.txt'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kanban'
}

# Проверка наличия файла и создание, если его нет
def initDb():
    if not os.path.exists(db_filename):
        data = {
            "users": [],
            "resumes": []
        }
        with open(db_filename, 'w', encoding='utf-8') as db_file:
            json.dump(data, db_file, indent=4)
        logAction("initDb", "Database initialized with empty tables.")
    else:
        print("База данных существует!")


# Функция логирования действий
def logAction(action, details):
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_entry = f"{datetime.now()} | Action: {action} | Details: {details}\n"
        log_file.write(log_entry)



import pymysql

def readFromDb(db, table, record_id=None, email=None, password=None, rid=None):
    connection = pymysql.connect(**db)
    try:
        with connection.cursor() as cursor:
            column = "resume_id" if rid == "resume_id" else "id"

            if email and password:
                cursor.execute(f"SELECT * FROM `{table}` WHERE `email` = %s AND `password` = %s", (email, password))
            else:
                cursor.execute(f"SELECT * FROM `{table}` WHERE `{column}` = %s", (record_id,))

            record = cursor.fetchone()
            if record is not None:
                columns = [col[0] for col in cursor.description]
                record_dict = dict(zip(columns, record))
                return record_dict
            else:
                return False
    finally:
        connection.close()


# Функция для получения всех записей из БД
def getAllRecords(db, table):
    connection = pymysql.connect(**db)
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM `{table}`")
        records = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, record)) for record in records]
        return result if result else "Записей нету"

# Функция для записи данных в БД
def writeToDb(db, table, params, record):
    try:
        connection = pymysql.connect(**db)
        with connection.cursor() as cursor:
            columns = ", ".join(f"`{param}`" for param in params)
            placeholders = ", ".join(["%s"] * len(params))
            sql = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"

            cursor.execute(sql, record)
            connection.commit()

            last_id = cursor.lastrowid
            return last_id
    except pymysql.MySQLError as e:
        print(f"Ошибка при добавлении записи: {e}")
        return None
    finally:
        connection.close()

# Функция для добавления пользователя
def addUser(db, name, surname, patronymic, email, password, role):
    new_user = (
        name,
        surname,
        patronymic,
        email,
        password,
        0,
        role
    )
    params = [
        "name", "surname", "patronymic", "email", "password", "verification", "role"
    ]
    return writeToDb(db, 'users', params, new_user)

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








# Функция для изменения объекта в базе данных
def updateInDb(db, table, record_id, updates, condition=None):
    connection = pymysql.connect(**db)

    try:
        with connection.cursor() as cursor:
            if condition:
                if condition == 3:  #
                    updates['additional_field'] = 'new_value' 
                    print(f"Условие выполнено для new_column == {condition}. Обновляем дополнительные данные.")

            set_clause = ", ".join([f"`{key}`=%s" for key in updates.keys()])
            sql = f"UPDATE `{table}` SET {set_clause} WHERE `id`=%s"
            values = list(updates.values()) + [record_id]

            print(f"SQL запрос: {sql}, Значения: {values}")  
            cursor.execute(sql, values) 
        
        connection.commit()  

    except Exception as e:
        print(f"Ошибка при обновлении записи: {e}")
        connection.rollback()  

    finally:
        connection.close()

def updateInDbGlass(db, table, record_id, updates):
    connection = pymysql.connect(**db)

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE `{table}` SET `glass`=%s WHERE `id`=%s", (updates, record_id))
        
        connection.commit() 
        return True
    except Exception as e:
        print(f"Ошибка при обновлении записи: {e}")
        connection.rollback() 

    finally:
        connection.close()
def updateFileInDb(db, resume_id, file_num, file_path):
    if 1 <= file_num <= 3:
        try:
            connection = pymysql.connect(**db)
            with connection.cursor() as cursor:
                    cursor.execute("UPDATE `resumes` SET `photo`='%s' WHERE `resume_id`='%s'", (file_path, resume_id,))

                    connection.commit()


        except pymysql.MySQLError as e:
            logAction("updateFileInDb", f"MySQL error: {e}")
            return False
        finally:
            connection.close()
    else:
        logAction("updateFileInDb", f"Invalid file number {file_num} for resume {resume_id}")
        return False

def deleteFromDb(db, table, record_id):
    connection = pymysql.connect(**db)
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM `{table}` WHERE `id` = %s", (record_id,))
        
        connection.commit()  
        print(f"Record with ID {record_id} deleted successfully from {table}.")
        return True
    except Exception as e:
        print(f"Error while deleting record: {e}")
        connection.rollback() 
        return False
    finally:
        connection.close()


def getTagsForResume(resume_id, db_config):
    connection = pymysql.connect(**db_config)
    tags_data = []
    
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM `tags` WHERE `resume_id` = %s", (resume_id,))
            tags_data = cursor.fetchall() 
    finally:
        connection.close()
    
    return tags_data


def tagExists(db, tag_name, resume_id):
    connection = pymysql.connect(**db)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM tags WHERE name = %s AND resume_id = %s", (tag_name, resume_id))
            result = cursor.fetchone()  
            return result[0] > 0 
    finally:
        connection.close()

def addTag(db, skill, resume_id):
    try:
        connection = pymysql.connect(**db)
        with connection.cursor() as cursor:
            query = """
                INSERT INTO tags (resume_id, name)
                VALUES (%s, %s)
            """
            params = (resume_id, skill)
            cursor.execute(query, params)
            connection.commit() 
    except pymysql.MySQLError as e:
        print(f"Ошибка при добавлении тега: {e}")
    finally:
        connection.close()  
        
def removeTag(db, tagid, resume_id):
    try:
        connection = pymysql.connect(**db)
        
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tags WHERE `id` = %s AND `resume_id` = %s", (tagid, resume_id))
            
            connection.commit()
            
            affected_rows = cursor.rowcount
            if affected_rows > 0:
                return {"success": True, "message": f"Tag with ID {tagid} removed successfully."}
            else:
                return {"success": False, "message": "No tag found with the provided ID and resume_id."}
    
    except pymysql.MySQLError as e:
        return {"success": False, "message": f"Database error: {str(e)}"}
    
    finally:
        connection.close()



def addFileResume(db, resume_id, file_url, mode):
    """
    Добавляет файл в таблицу files
    """
    connection = pymysql.connect(**db)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO `files` (resume_id, file_url, mode) VALUES (%s, %s, %s)",
                (resume_id, file_url, mode)
            )
            connection.commit()
        return True
    except Exception as e:
        print(f"Ошибка добавления файла в базу данных: {e}")
        return False
    finally:
        connection.close()



def getFileResume(db, resume_id, file_mode):
    connection = pymysql.connect(**db)

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT file_url FROM `files` WHERE resume_id=%s AND mode=%s", (resume_id, file_mode)
            )
            files = cursor.fetchall()
            return [file['file_url'] for file in files]
    except Exception as e:
        print(f"Ошибка получения файлов: {e}")
        return []  
    finally:
        connection.close()







def updateResumePhoto(db, resume_id, photo):
    connection = pymysql.connect(**db)

    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE `resumes` SET `photo`=%s WHERE `id`=%s", (photo, resume_id))
        
        connection.commit()  # Сохраняем изменения в базе данных
        print(f"Фото для резюме {resume_id} обновлено на {photo}")  # Логируем успех
        return True

    except Exception as e:
        print(f"Ошибка при обновлении фотографии: {e}")
        connection.rollback()  # Откатываем изменения в случае ошибки
        return False

    finally:
        connection.close()

def updateResumePhoto(db, resume_id, photo):
    connection = pymysql.connect(**db)

    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE `resumes` SET `photo`=%s WHERE `id`=%s", (photo, resume_id))
        
        connection.commit()  # Сохраняем изменения в базе данных
        print(f"Фото для резюме {resume_id} обновлено на {photo}")  # Логируем успех
        return True

    except Exception as e:
        print(f"Ошибка при обновлении фотографии: {e}")
        connection.rollback()  # Откатываем изменения в случае ошибки
        return False

    finally:
        connection.close()


def updateFileInDb(db, resume_id, file_number, file_path):
    connection = pymysql.connect(**db)

    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE `files` SET `file_path`=%s WHERE `resume_id`=%s AND `file_number`=%s", (file_path, resume_id, file_number))
        
        connection.commit() 
        return True
    except Exception as e:
        print(f"Ошибка при обновлении файла: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def hash_password(text: str, algorithm: str = 'sha256') -> str:
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()


def get_time_ago(date_string):
    date_object = datetime.strptime(str(date_string), "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(date_object.timetuple())
    current_time = time.time()
    hours_ago = (current_time - timestamp) / 3600  
    
    return hours_ago

def get_current_time_in_moscow():
    moscow_tz = pytz.timezone("Europe/Moscow")
    
    current_time_msk = datetime.now(moscow_tz)
    
    return current_time_msk.strftime("%Y-%m-%d %H:%M:%S")



def generate_activation_code(length=6):
    characters = string.ascii_letters + string.digits  # Буквы и цифры
    code = ''.join(secrets.choice(characters) for i in range(length))
    return code


def save_code(db, code, user_id):
    try:
        connection = pymysql.connect(**db)
        
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO `activation_codes`(user_id, code, status) VALUES(%s, %s, %s)", (user_id, code, 0))
            
            connection.commit()
            print("Код активации успешно сохранен!")
    
    except Exception as e:
        print(f"Ошибка при сохранении кода активации: {e}")
    
    finally:
        connection.close()

def fileExist(db, mode, resume_id):
    try:
        connection = pymysql.connect(**db)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM `files` WHERE `mode` = %s AND `resume_id` = %s", (mode, resume_id))
            result = cursor.fetchone()
            print(f"Результат запроса для mode={mode}, resume_id={resume_id}: {result}")
        return result
    except Exception as e:
        print("Ошибка в fileExist: {e}")
        return None

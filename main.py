"""
This module handles the main functionality for the Pokemon app.
"""
import os, json, timeago
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, flash, redirect, url_for, make_response, jsonify
from database import initDb, addUser, addResume, readFromDb, updateInDb, getAllRecords, updateFileInDb, deleteFromDb

app = Flask(__name__)
app.secret_key = 'your_secret_key'
initDb()
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER_FILE = os.path.join('static', 'uploads', 'files')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(UPLOAD_FOLDER_FILE):
    os.makedirs(UPLOAD_FOLDER_FILE)

@app.template_filter('format_time')
def format_time(value):
    # Преобразуем строку даты в объект datetime
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")  # Пример формата даты
    return timeago.format(value, datetime.now())  # Возвращаем формат "час назад", "3 дня назад"

@app.before_request
def check_authentication():
    if request.endpoint in ['signin', 'signup', 'static']:
        return None
    
    # Получаем user_id из cookie
    user_cookie = request.cookies.get('user_id')

    # 1. Проверка: Есть ли cookie у пользователя
    if not user_cookie:
        flash("Пожалуйста, зарегистрируйтесь для доступа.")
        return redirect(url_for('signup'))

    # Преобразуем user_id в int, так как он будет храниться как строка
    user_id = int(user_cookie)

    # 2. Проверка аккаунта в базе данных
    user = readFromDb('users', user_id)
    if not user:
        flash("Такого аккаунта не существует, войдите в другой или создайте новый.")
        return redirect(url_for('signup'))

    # 3. Проверка верификации аккаунта
    if user.get('verification') == 0:
        flash("Аккаунт не верифицирован, войдите в новый.")
        return redirect(url_for('signin'))
    
@app.route('/')
def home():
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"

    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb('users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')

    # Определение названий колонок
    kanban_columns = {
        1: "Стакан резюме",
        2: "Теплый контакт",
        3: "Скрининг",
        4: "Интервью",
        5: "Проверка СБ",
        6: "Оффер"
    }

    # Извлечение резюме из БД и группировка по "glass"
    resumes = {column_id: [] for column_id in kanban_columns.keys()}
    all_resumes = getAllRecords('resumes')  # Функция для получения всех резюме

    for resume in all_resumes:
        column_id = resume.get('glass', 1)
        if column_id in resumes:
            # Преобразуем теги из строки JSON в список
            if resume.get('tag'):
                resume['tag'] = json.loads(resume['tag'])
            resumes[column_id].append(resume)

    return render_template(
        'index.html',
        user_name=user_name,
        kanban_columns=kanban_columns,
        resumes=resumes
    )

@app.route('/move_resume', methods=['POST'])
def move_resume():
    data = request.json
    resume_id = int(data['resume_id'])
    new_column = int(data['new_column'])

    # Обновляем поле "glass" в БД для данного резюме
    update_result = updateInDb('resumes', resume_id, {'glass': new_column})

    if update_result:
        # Загружаем данные резюме для проверки состояния файлов
        resume = readFromDb('resumes', resume_id)
        if not resume:
            return jsonify({"status": "error", "message": "Resume not found"}), 404

        message = None
        url = f"http://127.0.0.1:5000/resume/{resume_id}"  # Ссылка на само резюме
        
        # Проверка нового столбца и настройка сообщения
        if new_column == 3:
            message = "Пожалуйста, загрузите файл скрининга."
        elif new_column == 4:
            message = "Пожалуйста, загрузите файл результата собеседования."
        elif new_column == 6:
            message = "Пожалуйста, загрузите файл оффера (обязательный файл)."

        return jsonify({"status": "success", "message": message, "url": url}), 200
    return jsonify({"status": "error", "message": "Resume not found"}), 404

@app.route('/delete_resume/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    success = deleteFromDb('resumes', resume_id)  # Удаляем запись из БД
    if success:
        return '', 200  # Возвращаем успешный ответ
    else:
        return '', 404  # Возвращаем ошибку, если запись не найдена

@app.route('/logout')
def logout():
    # Удаляем cookie при выходе
    resp = make_response(redirect(url_for('signin')))
    resp.delete_cookie('user_id')
    flash("Вы вышли из аккаунта.")
    return resp

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        surname = request.form.get('surname')
        patronymic = request.form.get('patronymic')
        email = request.form.get('email')
        password = request.form.get('password')

        # Проверяем, существует ли пользователь с таким email
        existing_user = next((user for user in getAllRecords('users') if user.get('email') == email), None)
        if existing_user:
            flash("Пользователь с таким email уже существует.")
            return redirect(url_for('signup'))

        # Получаем максимальный ID пользователя и увеличиваем его на 1
        users = getAllRecords('users')
        if users:
            last_id = max(user['id'] for user in users)
            user_id = last_id + 1
        else:
            user_id = 1  # Начальный ID, если пользователей еще нет

        # Добавление нового пользователя в базу данных
        addUser(user_id, name, surname, patronymic, email, password)

        flash("Регистрация прошла успешно! Пожалуйста, войдите.")
        return redirect(url_for('signin'))
    
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"

    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb('users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')

    return render_template('signup.html', user_name=user_name)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Получаем данные из формы
        email = request.form.get('email')
        password = request.form.get('password')

        # Ищем пользователя с указанным email и паролем
        users = getAllRecords('users')
        user = next((u for u in users if u['email'] == email and u['password'] == password), None)

        # Проверяем, существует ли пользователь
        if user:
            # Проверяем, верифицирован ли пользователь
            if user.get('verification') == 1:
                # Успешный вход: создаем ответ с cookie
                response = make_response(redirect(url_for('home')))
                # Записываем ID пользователя в cookie с секретным ключом
                response.set_cookie('user_id', str(user['id']), httponly=True, secure=True)
                flash("Вы успешно вошли в аккаунт.")
                return response
            else:
                flash("Ваш аккаунт не верифицирован.")
                return redirect(url_for('signin'))
        else:
            flash("Неправильный email или пароль. Попробуйте снова.")
            return redirect(url_for('signin'))
        
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"

    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb('users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')
    
    return render_template('signin.html', user_name=user_name)

# Проверка расширения файла
def allowed_file_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/resume/<int:resume_id>', methods=['GET', 'POST'])
def resume(resume_id):
    resume_data = readFromDb("resumes", resume_id)
    
    if resume_data is None:
        flash("Резюме не найдено")
        return redirect(url_for('home'))
    
    # Преобразование тегов из строки JSON в список
    if resume_data.get('tag'):
        resume_data['tag'] = json.loads(resume_data['tag'])

    if request.method == 'POST':
        files_uploaded = False  # Флаг, показывающий, загружен ли файл

        for i in range(1, 4):
            file = request.files.get(f'file_{i}')
            if file:
                # Проверяем файл с функцией allowed_file
                if allowed_file(file.filename):
                    # Если файл прошёл проверку, сохраняем его с оригинальным именем
                    filename = secure_filename(file.filename)
                else:
                    # Если файл не прошёл проверку, создаем имя {id_resume}_file_{i}
                    filename = f"{resume_id}_file_{i}.{file.filename.rsplit('.', 1)[-1]}"
                
                # Путь для сохранения файла
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                
                # Создаём папку, если её нет
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                
                # Сохраняем файл
                file.save(file_path)

                # Обновляем путь файла в базе данных
                if updateFileInDb(resume_id, i, file_path):
                    flash(f"Файл {i} успешно загружен!")
                    files_uploaded = True
                else:
                    flash(f"Не удалось загрузить файл {i}.")

        # Перенаправляем на страницу с резюме после обработки POST-запроса
        if files_uploaded:
            return redirect(url_for('resume', resume_id=resume_id))

    # Получаем данные пользователя
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"

    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb('users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')

    return render_template('resume.html', resume=resume_data, user_name=user_name)

# Функция для проверки допустимого расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create', methods=['GET', 'POST'])
def create():
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"

    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb('users', user_id)
        if user:
            user_name_short = user.get('name', 'Пользователь')
            user_name = [user.get('surname', 'Пользователь'), user.get('name', 'Пользователь'), user.get('patronymic', 'Пользователь')]

    if request.method == 'POST':
        # Получаем данные из формы
        fio = request.form['fio']
        position = request.form['position']
        expected_salary = request.form['expected_salary']
        experience_years = request.form['experience_years']
        birth_date = request.form['birth_date']
        phone = request.form['phone']
        email = request.form['email']
        skills = request.form['skills']
        education = request.form['education']
        comment = request.form['comment']

        # Получаем максимальный ID резюме и увеличиваем его на 1
        resumes = getAllRecords('resumes')
        if resumes:
            last_id = max(resumes['id'] for resumes in resumes)
            resumes_id = last_id + 1
        else:
            resumes_id = 1

        # Превращение из фио в 3 переменные
        fio_parts = fio.split()

        if len(fio_parts) == 2:
            last_name, first_name = fio_parts
            middle_name = "" 
        elif len(fio_parts) == 3:
            last_name, first_name, middle_name = fio_parts
        else:
            flash("Пожалуйста, введите ФИО в формате: Фамилия Имя Отчество.")
            return redirect(url_for('create'))

        # Обрабатываем файл изображения (если он был загружен)
        file = request.files.get('photo')  # Замените 'photo' на имя вашего поля для загрузки

        if file and allowed_file(file.filename):
            # Генерация уникального имени для файла (например, img.id)
            filename = f"img.{str(resumes_id)}"  # Имя файла с id резюме
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Создание папки, если её нет
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            # Сохраняем изображение
            file.save(file_path)

            # Путь для сохранения в базу данных
            image_path = f"/static/uploads/img/{filename}"
        else:
            # Если файл не был загружен или он не поддерживаемого формата
            image_path = "/static/uploads/img/none.png"

        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Добавляем резюме в базу данных (передаем все данные, включая image_path)
        addResume(resumes_id, image_path, first_name, last_name, middle_name, position, expected_salary,
                experience_years, birth_date, phone, email,
                skills, education, comment, user_name, creation_date)

        flash("Резюме успешно создано!")
        return redirect(url_for('home'))  # Перенаправляем на главную страницу

    return render_template("create.html", user_name=user_name_short)

@app.route('/resume/edit/<int:resume_id>', methods=['GET', 'POST'])
def edit_resume(resume_id):
    # Получаем данные резюме
    resume_data = readFromDb("resumes", resume_id)
    
    if resume_data is None:
        flash("Резюме не найдено")
        return redirect(url_for('home'))
    
    # Преобразуем теги из строки JSON в список
    if resume_data.get('tag'):
        resume_data['tag'] = json.loads(resume_data['tag'])

    # Обработка формы для изменения резюме
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name', resume_data.get('name'))
        surname = request.form.get('surname', resume_data.get('surname'))
        patronymic = request.form.get('patronymic', resume_data.get('patronymic'))
        post = request.form.get('post', resume_data.get('post'))
        salary = request.form.get('salary', resume_data.get('salary'))
        experience = request.form.get('experience', resume_data.get('experience'))
        dateBirth = request.form.get('dateBirth', resume_data.get('dateBirth'))
        telephone = request.form.get('telephone', resume_data.get('telephone'))
        email = request.form.get('email', resume_data.get('email'))
        education = request.form.get('education', resume_data.get('education'))
        comment = request.form.get('comment', resume_data.get('comment'))
        
        # Обновляем данные в базе данных
        updates = {
            "name": name,
            "surname": surname,
            "patronymic": patronymic,
            "post": post,
            "salary": salary,
            "experience": experience,
            "dateBirth": dateBirth,
            "telephone": telephone,
            "email": email,
            "education": education,
            "comment": comment
        }
        
        # Обновляем резюме в базе данных
        if updateInDb("resumes", resume_id, updates):
            flash("Резюме обновлено успешно!")
        
        # Обработка загрузки файлов
        files_uploaded = False  # Флаг, показывающий, что файл был загружен
        for i in range(1, 4):
            file = request.files.get(f'file_{i}')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                
                # Создаём папку, если её нет
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                
                file.save(file_path)

                # Обновляем путь файла в базе данных
                if updateFileInDb(resume_id, i, file_path):
                    flash(f"Файл {i} успешно загружен!")
                    files_uploaded = True
                else:
                    flash(f"Не удалось загрузить файл {i}.")

        # Перенаправляем на страницу с резюме после обработки POST-запроса
        if files_uploaded:
            return redirect(url_for('resume', resume_id=resume_id))
        else:
            return redirect(url_for('edit_resume', resume_id=resume_id))

    # Получаем данные пользователя
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"
    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb('users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')

    return render_template('edit_resume.html', resume=resume_data, user_name=user_name)


if __name__ == '__main__':
    app.run(debug=True)

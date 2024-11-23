"""
This module handles the main functionality for the Pokemon app.
"""
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pymysql
import os, json, timeago
import smtplib
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, flash, redirect, url_for, make_response, jsonify
from database import addTag, fileExist, initDb, addUser, addResume, readFromDb, updateInDb, updateInDbGlass, getAllRecords
from database import hash_password, updateFileInDb, deleteFromDb, getFileResume, addFileResume,getTagsForResume, updateResumePhoto
from database import get_time_ago, removeTag, tagExists, generate_activation_code, save_code
from colorama import Fore, init

init()

app = Flask(__name__)
app.secret_key = 'kanban2024$'
initDb()
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'img')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', "docx", "doc", "exel"}
UPLOAD_FOLDER_FILE = os.path.join('static', 'uploads', 'files')
moder_mail = 'nikitarybalko897@gmail.com'
# readFromDb

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kanban'
}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(UPLOAD_FOLDER_FILE):
    os.makedirs(UPLOAD_FOLDER_FILE)

def send_email(db, user_id):
    try:
        # Подключение к базе данных
        connection = pymysql.connect(**db)
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Получение email всех модераторов
            cursor.execute("SELECT email FROM `users` WHERE `role`=%s", ("moderator",))
            moderators = cursor.fetchall()

        # Отправка писем каждому модератору
        for moderator in moderators:
            receiver_email = moderator["email"]
            user = readFromDb(DB_CONFIG, 'users', user_id)
            email = user.get('email')
            
            # Настройка SMTP
            s = smtplib.SMTP("smtp.mail.ru", 587)
            s.starttls()
            s.login("hello@irminsul.space", "MBsmFgciJC5nGzTsj7vf")

            # Формирование сообщения
            msg = MIMEMultipart()
            msg['From'] = 'hello@irminsul.space'
            msg['To'] = receiver_email
            msg['Subject'] = f"Верификация на сайте: Новый пользователь {receiver_email}"

            # Тело письма
            body = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            color: #333;
                        }}
                        table {{
                            width: 100%;
                            max-width: 600px;
                            margin: auto;
                            padding: 20px;
                            background-color: white;
                            border-radius: 8px;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        }}
                        h2 {{
                            color: #007BFF;
                        }}
                        p {{
                            margin: 0 0 10px;
                        }}
                        a {{
                            color: #007BFF;
                            text-decoration: none;
                            font-weight: bold;
                        }}
                        a:hover {{
                            text-decoration: underline;
                        }}
                    </style>
                </head>
                <body>
                    <table>
                        <tr>
                            <td>
                                <h2>Новый пользователь зарегистрировался</h2>
                                <p>Уважаемый модератор,</p>
                                <p>Зарегистрирован новый пользователь с данными:</p>
                                <p><b>Email:</b> {email}</p>
                                <p><b>ID пользователя:</b> {user_id}</p>
                                <p>Вы можете проверить профиль пользователя, перейдя по ссылке:</p>
                                <p><a href="{request.host_url}verification">Проверить профиль</a></p>
                                <p>С уважением,</p>
                                <p>Команда модерации</p>
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            # Отправка письма
            s.sendmail("hello@irminsul.space", receiver_email, msg.as_string())
            print(f"Письмо отправлено модератору: {receiver_email}")
            s.quit()

    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")




@app.template_filter('format_time')
def format_time(value):
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S") 
    return timeago.format(value, datetime.now()) 

@app.before_request
def check_authentication():
    # Получаем имя маршрута, с которого был выполнен запрос
    endpoint = request.endpoint

    # Исключаем проверку аутентификации для следующих маршрутов
    if endpoint in ['verify_account', 'signin', 'signup', 'static']:
        return None
    
    # Получаем user_id из cookie
    user_cookie = request.cookies.get('user_id')

    if not user_cookie:
        flash("Пожалуйста, зарегистрируйтесь для доступа.")
        return redirect(url_for('signup'))

    user_id = int(user_cookie)

    # 2. Проверка аккаунта в базе данных
    user = readFromDb(DB_CONFIG, 'users', user_id)
    if not user:
        flash("Такого аккаунта не существует, войдите в другой или создайте новый.")
        return redirect(url_for('signup'))

    # 3. Проверка верификации аккаунта
    if user.get('verification') == 0:
        flash("Аккаунт не верифицирован, войдите в новый.")
        return redirect(url_for('signin'))
    if user.get('verification') == 2:
        flash("Аккаунт заблокирован")
        return redirect(url_for('signin'))

@app.route('/')
def home():
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"
    user_role = 2

    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb(DB_CONFIG, 'users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')
            user_role = user.get('role', 'hr')
    
    kanban_columns = {
        1: "Стакан резюме",
        2: "Теплый контакт",
        3: "Скрининг",
        4: "Интервью",
        5: "Проверка СБ",
        6: "Оффер"
    }

    # Проверка наличия резюме в базе данных
    if readFromDb(DB_CONFIG, "resumes", 1) is False:
        resumes = {column_id: [] for column_id in kanban_columns.keys()}
    else:
        resumes = {column_id: [] for column_id in kanban_columns.keys()}

        # Извлекаем все резюме
        all_resumes = getAllRecords(DB_CONFIG, 'resumes')  
        for resume in all_resumes:
            column_id = resume.get('glass', 1)

            if column_id in resumes:
                resume_id = resume.get('id') 
                tags = getAllRecords(DB_CONFIG, 'tags')  
                resume_tags = [tag['name'] for tag in tags if tag['resume_id'] == resume_id]

                resume['tag'] = resume_tags

                resumes[column_id].append(resume)

    print(Fore.RED + user_name)
    return render_template(
        'index.html',
        user_name=user_name,
        kanban_columns=kanban_columns,
        resumes=resumes,
        user_role=user_role
    )



@app.route('/move_resume', methods=['POST']) 
def move_resume(): 
    data = request.json 
    resume_id = int(data['resume_id']) 
    new_column = int(data['new_column']) 
     
    # Обновляем поле "glass" в БД для данного резюме 
    update_result = updateInDbGlass(DB_CONFIG, 'resumes', resume_id, new_column) 
 
    if update_result: 
        resume = readFromDb(DB_CONFIG, 'resumes', resume_id) 
        if not resume: 
            return jsonify({"status": "error", "message": "Resume not found"}), 404 
         
        message = ['Пожалуйста, загрузите файл'] 
        url = f"/resume/{resume_id}" 
 
        # Проверяем файлы, которые нужно загрузить для определённых колонок 
        if new_column == 3:  # Для колонки 3 требуется только файл скрининга (mode 1) 
            mode = 1 
            file_exist = fileExist(DB_CONFIG, mode, resume_id) 
            if not file_exist: 
                message.append('скрининга') 
 
        elif new_column == 4 or new_column == 5:  # Для колонок 4 и 5 требуется файл собеседования (mode 2) искрининга (mode 1) 
            # Проверка на файл собеседования (mode 2) 
            mode = 2
            file_exist = fileExist(DB_CONFIG, mode, resume_id) 
            if not file_exist: 
                message.append('результата собеседования') 
             
            # Проверка на файл скрининга (mode 1) 
            mode = 1
            file_exist = fileExist(DB_CONFIG, mode, resume_id) 
            if not file_exist: 
                message.append('скрининга') 
 
        elif new_column == 6:  # Для колонки 6 требуются все 3 файла: оффера (mode 3), собеседования (mode 2) и скрининга (mode 1) 
            # Проверка на файл оффера (mode 3) 
            mode = 3
            file_exist = fileExist(DB_CONFIG, mode, resume_id) 
            if not file_exist: 
                message.append('оффера (обязательный файл)') 
             
            # Проверка на файл результата собеседования (mode 2) 
            mode = 2
            file_exist = fileExist(DB_CONFIG, mode, resume_id) 
            if not file_exist: 
                message.append('результата собеседования') 
             
            # Проверка на файл скрининга (mode 1) 
            mode = 1
            file_exist = fileExist(DB_CONFIG, mode, resume_id) 
            if not file_exist: 
                message.append('скрининга') 
 
        elif new_column == 1 or new_column == 2:
            message = None 
 
        # Формируем ответ с сообщением 
        if len(message) > 2:  # Если список содержит больше одного элемента (первый элемент — общая фраза) 
            message = ', '.join(message)
 
        if message is not None: 
            print(f"Message: {message}") 
            return jsonify({"status": "success", "message": message, "url": url}), 200 
 
    return jsonify({"status": "error", "message": f"Resume not found: {resume_id}"}), 404


@app.route('/delete_resume/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    success = deleteFromDb(DB_CONFIG,'resumes', resume_id) 
    if success:
        return '', 200 
    else:
        return '', 404  

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
        password=hash_password(password)

        # Проверяем, существует ли пользователь с таким email
        existing_user = readFromDb(DB_CONFIG, "users",email=email, password=password)
        if existing_user:
            flash("Пользователь с таким email уже существует.")
            return redirect(url_for('signup'))


        # Добавление нового пользователя в базу данных
        addUser(DB_CONFIG, name, surname, patronymic, email, password, "hr")
        code = generate_activation_code(11)
        user = readFromDb(DB_CONFIG, "users", email=email, password=password)
        save_code(DB_CONFIG, code, user["id"])
        send_email(DB_CONFIG,user["id"])
        print(Fore.RED + "id: "+ str(user["id"]) + "\n" + code)
        flash("Регистрация завершена. Дождитесь верификации аккаунта")
        return redirect(url_for('signin'))
    
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"

    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb(DB_CONFIG,'users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')

    return render_template('signup.html', user_name=user_name)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Получаем данные из формы
        email = request.form.get('email')
        password = request.form.get('password')
        password=hash_password(password)
        # Ищем пользователя с указанным email и паролем
        users = getAllRecords(DB_CONFIG,'users')
        user = next((u for u in users if u['email'] == email and u['password'] == password), None)

        if email == moder_mail:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                cursor.execute("UPDATE `users` SET `role`=%s WHERE `id`=%s", ('moderator', user['id']))
            connection.commit()

        if user:
            if user.get('verification') == 1:
                response = make_response(redirect(url_for('home')))
                response.set_cookie('user_id', str(user['id']), httponly=True, secure=True)
                flash("Вы успешно вошли в аккаунт.")
                return response
            else:
                flash("Аккаунт не верифицирован. Обратитесь к менеджеру")
                return redirect(url_for('signin'))
        else:
            flash("Неправильный email или пароль. Попробуйте снова.")
            return redirect(url_for('signin'))
        
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"

    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb(DB_CONFIG,'users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')
    
    return render_template('signin.html', user_name=user_name)

# Проверка расширения файла
def allowed_file_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/resume/<int:resume_id>', methods=['GET', 'POST'])
def resume(resume_id):
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"
    user_role = 2

    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb(DB_CONFIG, 'users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')
            user_role = user.get('role', 'hr')

    # Получаем данные резюме
    resume_data = readFromDb(DB_CONFIG, "resumes", resume_id)
    
    if not resume_data:
        flash("Резюме не найдено")
        return redirect(url_for('home'))
    if request.method == 'POST':
        for i in range(1, 4): 
            file = request.files.get(f'file_{i}')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                file.save(file_path)
                addFileResume(DB_CONFIG, resume_id, file_path, i)

        flash("Файлы успешно загружены!")
        return redirect(url_for('resume', resume_id=resume_id))
    app.jinja_env.globals['files'] = getFileResume
    date_string = resume_data["creation_date"]
    hours = get_time_ago(date_string)
    skills=getTagsForResume(resume_id, DB_CONFIG)

    return render_template('resume.html', resume=resume_data, db=DB_CONFIG, date=get_time_ago(resume_data["creation_date"]), skills=skills, user_name=user_name, user_role=user_role)


@app.route("/verification", methods=["GET"])
def verification():
    users=getAllRecords(DB_CONFIG, "users")
    username=readFromDb(DB_CONFIG, "users", request.cookies.get('user_id'))
    if username["role"] == "moderator":
        return render_template("verification.html", users=users, user_name=username['name'], user_role=username['role'])
    else:
        return redirect(url_for("home"))





# Функция для проверки допустимого расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/create', methods=['GET', 'POST'])
def create():
    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"
    user_role = 2

    # Проверка пользователя
    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb(DB_CONFIG, 'users', user_id)
        if user:
            user_name = f"{user.get('name', 'Пользователь')}"
            user_role = user.get('role', 'hr')

    if request.method == 'POST':
        # Получаем данные из формы
        fio = request.form.get('fio', '')
        position = request.form.get('position', '')
        expected_salary = request.form.get('expected_salary', 0)
        experience_years = request.form.get('experience_years', 0)
        birth_date = request.form.get('birth_date', '')
        phone = request.form.get('phone', '')
        email = request.form.get('email', '')
        skills = request.form['skills']
        education = request.form.get('education', '')
        comment = request.form.get('comment', '')
        file = request.files.get('photo')
        
        # Проверяем наличие фото
        if not file or not file.filename:
            flash("Пожалуйста, добавьте фотографию.")
            return redirect(url_for('create'))

        fio_parts = fio.split()
        if len(fio_parts) == 2:
            last_name, first_name = fio_parts
            middle_name = ""
        elif len(fio_parts) == 3:
            last_name, first_name, middle_name = fio_parts
        else:
            flash("Введите ФИО в формате: Фамилия Имя Отчество.")
            return redirect(url_for('create'))

        # Проверяем допустимость файла
        if not allowed_file(file.filename):
            flash("Недопустимый формат файла. Загрузите изображение в формате JPG, PNG.")
            return redirect(url_for('create'))

        # Загрузка файла
        resumes = getAllRecords(DB_CONFIG, 'resumes')

        if not resumes:
            last_id = 0
        else:
            try:
                last_id = max((resume['id'] for resume in resumes if isinstance(resume, dict)), default=0)
            except KeyError:
                flash("Ошибка при получении данных из базы.")
                return redirect(url_for('create'))
            except TypeError:
                flash("Некорректные данные в базе.")
                return redirect(url_for('create'))

        resumes_id = last_id + 1

        filename = f"img-{resumes_id}.jpg"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(file_path)
        image_path = f"/static/uploads/img/{filename}"

        # Записываем дату создания
        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Сохраняем резюме в базу
        result = addResume(
            image_path,
            last_name,
            first_name,
            middle_name,
            position,
            int(expected_salary),
            int(experience_years),
            birth_date,
            phone,
            email,
            education,
            comment,
            user_name,
            creation_date
        )

        # Добавляем теги
        skills = json.loads(skills)
        for skill in skills:
            addTag(DB_CONFIG, skill, resumes_id)

        flash("Резюме успешно создано!")
        return redirect(url_for('home'))

    # GET-запрос: отображение страницы создания
    return render_template("create.html", user_name=user_name, user_role=user_role)





@app.route('/resume/edit/<int:resume_id>', methods=['GET', 'POST'])
def edit_resume(resume_id):
    resume_data = readFromDb(DB_CONFIG, "resumes", resume_id)
    skills = getTagsForResume(resume_id, DB_CONFIG)

    if resume_data is None:
        flash("Резюме не найдено")
        return redirect(url_for('home'))
    
    if resume_data.get('tag'):
        try:
            resume_data['tag'] = json.loads(resume_data['tag'])
        except json.JSONDecodeError:
            resume_data['tag'] = []  

    if request.method == 'POST':
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
        skills_form = request.form.getlist("skills")  # Множественные выбранные теги

        for skill in skills_form:
            if not tagExists(DB_CONFIG, skill, resume_id):
                tags=json.loads(skill)
                for tag in tags:
                    addTag(DB_CONFIG, tag, resume_id)

        updates = {
            "name": name,
            "surname": surname,
            "patronymic": patronymic,
            "position": post,
            "salary": salary,
            "experience": experience,
            "dateBirth": dateBirth,
            "telephone": telephone,
            "email": email,
            "education": education,
            "comment": comment,
        }

        if updateInDb(DB_CONFIG, "resumes", resume_id, updates):
            flash("Резюме обновлено успешно!")

        files_uploaded = False
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
                if updateFileInDb(DB_CONFIG, resume_id, i, file_path):
                    flash(f"Файл {i} успешно загружен!")
                    files_uploaded = True
                else:
                    flash(f"Не удалось загрузить файл {i}.")
        
        photo = request.files.get('photo')
        if photo and allowed_file(photo.filename):
            photo_filename = secure_filename(photo.filename)
            photo_path = os.path.join(UPLOAD_FOLDER, photo_filename)

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            photo.save(photo_path)

            if updateResumePhoto(DB_CONFIG, resume_id, "\\" + photo_path):
                flash("Фото обновлено успешно!")
                files_uploaded = True
            else:
                flash("Не удалось обновить фото.")
        
        if files_uploaded:
            return redirect(url_for('resume', resume_id=resume_id, skills=skills))
        else:
            return redirect(url_for('resume', resume_id=resume_id))

    user_cookie = request.cookies.get('user_id')
    user_name = "Нет входа"
    user_role = 2
    if user_cookie:
        user_id = int(user_cookie)
        user = readFromDb(DB_CONFIG, 'users', user_id)
        if user:
            user_name = user.get('name', 'Пользователь')
            user_role = user.get('role', 'hr')
    
    files = getFileResume(DB_CONFIG, resume_data["id"], 0)
    return render_template('edit_resume.html', resume=resume_data, user_name=user_name, files=files, skills=skills, user_role=user_role)


@app.route("/verify/<int:userId>/<string:code>", methods=["GET"])
def verify_account(userId, code):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM `activation_codes` WHERE `user_id` = %s AND `status` = %s", (userId, 0))
            check_code = cursor.fetchone()

            if check_code and check_code[2] == code: 
                cursor.execute("UPDATE `activation_codes` SET `status` = %s WHERE `user_id` = %s AND `code` = %s", (1, userId, code))
                cursor.execute("UPDATE `users` SET `verification` = %s WHERE `id` =%s", (1,userId))
                connection.commit() 
                return redirect(url_for("home"))
            else:
                return "Неверный код активации или код не найден."

    except Exception as e:
        return f"Ошибка при верификации: {str(e)}"
    finally:
        connection.close()






@app.route("/remove_tag/<int:tagId>", methods=["POST"])
def delete_tag(tagId):
    resume_id = request.json.get('resume_id')

    if not resume_id:
        return jsonify({"error": "resume_id is required"}), 400
    
    removeTag(DB_CONFIG, tagId, resume_id)
    return jsonify({"resume_id": resume_id})

@app.route('/account/<action>/<int:user_id>', methods=['POST'])
def account_action(action, user_id):
    data = request.get_json()
    account_id = data.get('accountId')
    
    if not account_id:
        return jsonify({'success': False, 'message': 'ID аккаунта отсутствует.'})
    verification=None
    if action == 'verify':
        verification = 1
    elif action == 'unverify':
        verification=0
    elif action == 'block':
        verification=2
    elif action == 'unblock':
        verification = 3
    else:
        return jsonify({'success': False, 'message': 'Неизвестное действие.'})
    connection=pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        cursor.execute("UPDATE `users` SET `verification`=%s WHERE `id`=%s", (verification, user_id))
    connection.commit()
    return jsonify({'success': True, 'message': f'Действие "{action}" выполнено успешно.'})


@app.route('/update-role', methods=['POST'])
def update_role():
    data = request.json
    account_id = data.get('account_id')
    new_role = data.get('role')
    role=None
    if int(new_role) == 1:
        role = "moderator"
    elif int(new_role) == 2:
        role="hr"
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        cursor.execute("UPDATE `users` SET `role`=%s WHERE `id`=%s", (role, account_id))
    connection.commit()
    return jsonify({'message': 'Роль обновлена', 'account_id': account_id, 'role': new_role})


if __name__ == '__main__':
    app.run(debug=True)

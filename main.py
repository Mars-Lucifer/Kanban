"""
This module handles the main functionality for the Pokemon app.
"""
import os
from flask import Flask, request, render_template, flash, redirect, url_for
from database import init_db, add_user, add_resume, read_from_db


app = Flask(__name__)
app.secret_key = 'your_secret_key'
init_db()

@app.before_request
def check_authentication():
    if request.endpoint in ['signin', 'signup', 'static']:
        return None
    
    # Получаем cookie
    user_cookie = request.cookies.get('user_id')

    # 1. Проверка: Есть ли cookie у пользователя
    if not user_cookie:
        flash("Пожалуйста, зарегистрируйтесь для доступа.")
        return redirect(url_for('signup'))

    # 2. Проверка аккаунта в cookie (здесь заглушка)
    account_exists = True  # допустим, аккаунт в базе данных есть
    account_verified = False  # допустим, аккаунт не верифицирован

    if not account_exists:
        flash("Такого аккаунта не существует, войдите в другой или создайте новый.")
        return redirect(url_for('signup'))

    if not account_verified:
        flash("Аккаунт не верифицирован, войдите в новый.")
        return redirect(url_for('signin'))
    
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/resume')
def resume():
    return render_template('/resume.html')

@app.route('/create')
def create():
    return render_template('/create.html')


if __name__ == '__main__':
    app.run(debug=True)

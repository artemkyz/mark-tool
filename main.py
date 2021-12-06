from flask import Flask, request, session, redirect, url_for, render_template
import os.path
from datetime import datetime
import uuid

import utils
from actions.unify_self_signs import document
import emailer
from db_utils import new_base, commit_new_user, commit_temp_user, check_user_credentials, check_user_exist, \
    marked_furs, check_user_token, delete_temp_user
from config import dbase, secret_key, admin_email, documents_directory, domain_name

app = Flask(__name__)
app.secret_key = secret_key
app.config['UPLOAD_FOLDER'] = documents_directory

if os.path.isfile(dbase) is False:  # проверка на существующую базу
    new_base()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        date = datetime.now().timestamp()
        gln = request.form['gln']
        password = request.form['password']
        email = request.form['email']
        check_user = check_user_exist(gln, password)
        if check_user is True:
            message = '<p style="color:green; text-align:center; margin:0;">Пользователь с таким GLN уже ' \
                      'зарегистрирован, <a href="/login">войти</a>?</p> '
            return render_template('registration.html', message=message)

        token = uuid.uuid4().hex
        emailer.send_registration(admin_email, email, domain_name, token)
        commit_temp_user(date=date, gln=gln, password=password, email=email, token=token)
        message = f'<p style="text-align:center; margin:0;">Для завершения регистрации проверьте почту {email} ' \
                  f'и перейдите по ссылке из письме</p> '
        return render_template('login.html', message=message)

    return render_template('registration.html')


@app.route('/confirm_registration', methods=['GET'])
def confirm_registration():
    user_token = request.args.get('token')
    if user_token is None:
        return "refused by server", 200

    user_statement = check_user_token(user_token)
    if user_statement is False:
        return "failed", 200

    date_diff = datetime.now().timestamp() - float(user_statement[0])  # с момента регистрации должно пройти не
    # больше 86400 секунд
    if date_diff < 86400:
        # commit_new_user(timestamp, gln, password, email)
        commit_new_user(user_statement[0], user_statement[1], user_statement[2], user_statement[3])
        delete_temp_user(user_statement[1])
        message = f'<p style="color:green; text-align:center; margin:0;">Регистрация успешно завершена.<br> ' \
                  f'Используйте номер GLN и пароль для входа в систему</p> '
        return render_template('login.html', message=message)

    else:
        # Удалить запись в таблице временного пользователя и предложить регистрацию снова
        delete_temp_user(user_statement[1])
        message = f'<p style="color:green; text-align:center; margin:0;">Срок подтверждения регистрации истёк.' \
                  f'<br>Повторите регистрацию снова</p> '

        render_template('registration.html', message=message)
        pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        try:
            if session['gln']:  # сессия есть - редирект в ЛК
                return redirect(url_for('area'))
        except KeyError:
            return render_template('login.html')  # сессии нет - страница входа

    if request.method == 'POST':
        gln = request.form['gln']
        password = request.form['password']
        check_credentials = check_user_credentials(gln, password)

        if check_credentials is True:
            session['gln'] = request.form['gln']
            return redirect(url_for('area'))

        message = '<p style="color:red; text-align:center; margin:0;">Неверный GLN или пароль</p>'
        return render_template('login.html', message=message)


@app.route('/area', methods=['GET', 'POST'])
def area():
    if request.method == 'GET':
        try:
            if session['gln']:
                return render_template('area.html')
        except KeyError:
            return redirect(url_for('login'))


@app.route('/logout')
def delete_gln():
    session.pop('gln', default=None)
    return redirect(url_for('index'))


@app.route('/action20', methods=['POST'])
def action13():
    if request.method == 'POST':
        product_t = request.form['product_type']
        gln = session['gln']
        email = request.form['email']

        statement = utils.diff_user_input(dict(request.values))
        if statement[0] is False:
            return render_template('area.html', message=statement[1])

        try:
            document(gln, statement[1], product_t)
            emailer.send_document(admin_email, email,documents_directory, gln)
            message = f'<p style="color:green; text-align:center; margin:0;">' \
                      f'Документ успешно отправлен на почту {email}</p> '

            return render_template('area.html', message=message)

        except ValueError:
            message = '<p style="color:red; text-align:center; margin:0;">Введены неверные данные</p>'
            return render_template('area.html', message=message)


@app.route('/marked', methods=['GET'])
def marked():
    gln = session['gln']
    data = marked_furs(gln)

    if data is False:
        message = '<p style="color:red; text-align:center; margin:0;">Маркированная продукция отсутствует</p>'
        return render_template('marked.html', message=message)

    return render_template('marked.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)

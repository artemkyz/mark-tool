from flask import Flask, request, session, redirect, url_for, render_template
import os.path
from datetime import datetime
import uuid

from db_utils import new_base, commit_new_user, commit_temp_user, check_user_credentials, check_user_exist, \
    commit_fur, marked_furs, check_user_token, delete_temp_user
from config import dbase, secret_key, admin_email, documents_directory, domain_name
from emailer import send_mail
from actions.action13 import document13


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
        check_user = check_user_exist(gln=gln)
        if check_user is True:
            message = '<p style="color:green; text-align:center; margin:0;">Пользователь с таким GLN уже ' \
                      'зарегистрирован, <a href="/login">войти</a>?</p> '
            return render_template('registration.html', message=message)

        token = uuid.uuid4().hex
        print(token)
        send_mail(send_from=admin_email, send_to=[email], subject='Регистрация Маркировка',
                  text=f'Для подтверждения регистрации на сайте mark-tool перейдите по ссылке https:\\\{domain_name}\\'
                       f'confirm_registration\\{token} '
                       f'В случае если это письмо ошибочно попало в Ваш почтовый ящик просто удалите его.')
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

    print(user_statement)
    date_diff = datetime.now().timestamp() - float(user_statement[0])  # с момента регистрации должно пройти не
    # больше 86400 секунд
    print(date_diff)
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


@app.route('/action13', methods=['POST'])
def action13():
    if request.method == 'POST':
        gtin = request.form['gtin'].splitlines()
        kiz = request.form['kiz'].splitlines()
        tid = request.form['tid'].splitlines()
        product_t = request.form['product_type']
        gln = session['gln']
        email = request.form['email']

        if len(gtin) != len(kiz) or len(gtin) != len(tid) or len(kiz) != len(gtin) or len(kiz) != len(tid) \
                or len(tid) != len(gtin) or len(tid) != len(kiz):
            message = '<p style="color:red; text-align:center; margin:0;">Количество gtin, kiz и tid не совпадают</p>'
            return render_template('area.html', message=message)

        try:
            data = document13(gln, gtin, kiz, tid, product_t)
            send_mail(send_from=admin_email, send_to=[email], subject='Маркировка',
                      text='во вложении документ для маркировки шуб', files=[f'{documents_directory}/{gln}.xml'])
            message = f'<p style="color:green; text-align:center; margin:0;">' \
                      f'Документ успешно отправлен на почту {email}</p> '
            commit_fur(data)

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

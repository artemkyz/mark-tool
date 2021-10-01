from flask import Flask, render_template
from flask import request
from flask import send_from_directory
from User import document


UPLOAD_FOLDER = 'uploads'
FormHandler = Flask(__name__)
FormHandler.session_cookie_name = 'action13'
FormHandler.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@FormHandler.route('/', methods=['GET'])
def hello_world():
    return render_template('index.html')


@FormHandler.route('/action13', methods=['POST'])
def action13():
    try:
        response = dict(request.form)
        email = response['email']
        gln = response['gln']
        gtin = response['gtin'].split(' ')
        kiz = response['kiz'].split(' ')
        tid = response['tid'].split(' ')
        product_t = response['product_type']

        # Проверяем отправленные данные пользователя
        if gln and gtin and kiz and tid == '':
            comment = f'gln: {gln}; gtin: {gtin}; kiz: {kiz} ; tid: {tid};'
            return render_template('service_msg.html', reason='Отсутствуют данные', comment=comment)

        if len(gtin) != len(kiz) or len(gtin) != len(tid) or len(kiz) != len(gtin) or len(kiz) != len(tid) \
                or len(tid) != len(gtin) or len(tid) != len(kiz):
            comment = 'Количество gtin, kiz и tid не совпадают'
            return render_template('service_msg.html', reason='Отсутствуют данные', comment=comment)

        document(gln, gtin, kiz, tid, product_t)
        return send_from_directory(UPLOAD_FOLDER, f'{gln}.xml', as_attachment=True)

    except ValueError as error:
        print(error)
        return render_template('service_msg.html', reason=error)

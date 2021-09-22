from flask import Flask
from flask import request
from flask import flash
from flask import redirect
from flask import send_from_directory
from flask import render_template
from werkzeug.utils import secure_filename
from marking import *
import os
from pathlib import Path


UPLOAD_FOLDER = '/home/pi/projects/marking/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        GLN = request.form.get('GLN')
        prod_type = request.form.get('product_type')
        print(prod_type)
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            reason = 'Не был выбрал файл для отправки на сервер.'
            comment = 'Укажите файл с расширением <b>xlsx</b> с данными для маркировки и повторите попытку.'
            return render_template('error.html', reason=reason, comment=comment)

        # if user not choose a file
        elif file and not allowed_file(file.filename) or GLN == '':
            if file and not allowed_file(file.filename):
                reason = 'Не был выбрал файл для отправки на сервер.'
                comment = 'Укажите файл с расширением <b>xlsx</b> с данными для маркировки и повторите попытку.'
                return render_template('error.html', reason=reason, comment=comment)

            elif GLN == '':
                reason = 'Не был указан номер GLN.'
                comment = 'Укажите номер GLN.'
                return render_template('error.html', reason=reason, comment=comment)

        # handler user file and return report
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            Path(os.path.join(app.config['UPLOAD_FOLDER'], GLN)).mkdir(parents=True, exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], GLN, filename))

            user_file = os.path.join(app.config['UPLOAD_FOLDER'], GLN, filename)
            report = create_report(user_file)
            try:
                action20(report, GLN, prod_type)
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], GLN),
                                        'unify_self_signs.xml', as_attachment=True)

            except ValueError:
                reason = 'Выбранный файл имеет ошибки.'
                comment = 'Проверьте содержимое файла. Убедтесь что количество GTIN совпадает с количеством КИЗ.'
                return render_template('error.html', reason=reason, comment=comment)

    return render_template('index.html')


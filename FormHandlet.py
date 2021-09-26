from flask import Flask, render_template
from flask import request
from flask import send_from_directory
from lxml import etree
import os
from datetime import datetime
import lxml.builder


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
        print(response)

        if (response['gln'] and response['gtin'] and response['tid']) == '':
            return render_template('error.html', reason='Отсутствуют некоторые вводные данные')

        # if response['gtin'] == '':
        #     return render_template('error.html', reason='отсутствует GTIN')
        #
        # if response['tid'] == '':
        #     return render_template('error.html', reason='отсутствует КИЗ')

        gln = response['gln']
        gtin = response['gtin'].split(' ')
        tid = response['tid'].split(' ')
        product_t = response['product_type']

        if len(gtin) != len(tid):
            if len(gtin) < len(tid):
                return render_template('error.html', reason='Количество GTIN меньше TID')

            elif len(gtin) > len(tid):
                return render_template('error.html', reason='Количество TID меньше GTIN')

        # Создаем словарь, в котором будем хранить полученные данные.
        # Первичным ключом станет номер GLN,
        furs = dict(zip(gtin, tid))

        d = dict()
        # Преобразуем gtin в бинарный вид, учитывая правила. См. документацию по SGTIN96
        for gtin in furs.keys():
            gln_binary = bin(int(gtin[0:8]))[2:].rjust(30, '0')
            product_binary = bin(int(gtin[9:12]))[2:].rjust(14, '0')
            tid = furs.get(gtin)
            tid_bin = str(bin(int(str(tid), 16)))[2:]

            # Проверка производителя чипа и преобразование tid
            # Сюда дописывать условия генерации ключа ТИД в зависимости от производителя чипа
            if ('11100010000000000110100000001010' or '11100010000000000110100000001011' or '11100010100000000110110100010010' or '11100010100000000110110110010010') in tid_bin:
                tid_bin = '111' + tid_bin[61:95]

            # Сложение полученных результатов в SGTIN96
            d[gtin] = [tid, '00110000001011' + gln_binary + '0' + product_binary + tid_bin]
        print(d)

        # Здесь идёт проверка условий для комиссионной, новой или возвратной продукции
        if product_t == '1':
            now = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
            xsd = 'http://www.w3.org/2001/XMLSchema'
            xsi = 'http://www.w3.org/2001/XMLSchema-instance'
            page = lxml.builder.ElementMaker(
                nsmap={
                    "xsd": xsd,
                    "xsi": xsi
                }
            )
            root = page.query
            page = root()
            page.attrib['version'] = '2.41'
            page.attrib['{{{pre}}}noNamespaceSchemaLocation'.format(pre=xsi)] = '..\\xsd_new1\\query.xsd'
            unify_self_signs = etree.SubElement(page, "unify_self_signs")
            unify_self_signs.attrib['action_id'] = '20'
            sender_gln = etree.SubElement(unify_self_signs, "sender_gln")
            sender_gln.text = gln
            unify_date = etree.SubElement(unify_self_signs, "unify_date")
            unify_date.text = now
            unifies = etree.SubElement(unify_self_signs, "unifies")
            for key in d.keys():
                by_gtin = etree.SubElement(unifies, "by_gtin")
                sign_gtin = etree.SubElement(by_gtin, "sign_gtin")
                sign_gtin.text = key
                union = etree.SubElement(by_gtin, "union")
                gs1_sgtin = etree.SubElement(union, "gs1_sgtin")
                gs1_sgtin.text = d.get(key)[1]
                sign_num = etree.SubElement(union, "sign_num")
                sign_num.text = d.get(key)[0]
                product_type = etree.SubElement(union, "product_type")
                product_type.text = str(product_t)
            doc = etree.ElementTree(page)
            doc.write(f"{UPLOAD_FOLDER}/{gln}.xml", pretty_print=True)
            return send_from_directory(UPLOAD_FOLDER,
                                       f'{gln}.xml', as_attachment=True)

        elif product_t == '0':
            now = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
            xsd = 'http://www.w3.org/2001/XMLSchema'
            xsi = 'http://www.w3.org/2001/XMLSchema-instance'
            page = lxml.builder.ElementMaker(
                nsmap={
                    "xsd": xsd,
                    "xsi": xsi
                }
            )
            root = page.query
            page = root()
            page.attrib['version'] = '2.41'
            page.attrib['{{{pre}}}noNamespaceSchemaLocation'.format(pre=xsi)] = '..\\xsd_new1\\query.xsd'
            unify_self_signs = etree.SubElement(page, "unify_self_signs")
            unify_self_signs.attrib['action_id'] = '20'
            sender_gln = etree.SubElement(unify_self_signs, "sender_gln")
            sender_gln.text = gln
            unify_date = etree.SubElement(unify_self_signs, "unify_date")
            unify_date.text = now
            unifies = etree.SubElement(unify_self_signs, "unifies")
            for key in d.keys():
                by_gtin = etree.SubElement(unifies, "by_gtin")
                sign_gtin = etree.SubElement(by_gtin, "sign_gtin")
                sign_gtin.text = key
                union = etree.SubElement(by_gtin, "union")
                gs1_sgtin = etree.SubElement(union, "gs1_sgtin")
                gs1_sgtin.text = d.get(key)[1]
                sign_num = etree.SubElement(union, "sign_num")
                sign_num.text = d.get(key)[0]
                product_type = etree.SubElement(union, "product_type")
                product_type.text = str(product_t)
            doc = etree.ElementTree(page)
            doc.write(f"{UPLOAD_FOLDER}/{gln}.xml", pretty_print=True)
            return send_from_directory(UPLOAD_FOLDER,
                                       f'{gln}.xml', as_attachment=True)

        elif product_t == '2':
            now = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
            xsd = 'http://www.w3.org/2001/XMLSchema'
            xsi = 'http://www.w3.org/2001/XMLSchema-instance'
            page = lxml.builder.ElementMaker(
                nsmap={
                    "xsd": xsd,
                    "xsi": xsi
                }
            )
            root = page.query
            page = root()
            page.attrib['version'] = '2.41'
            page.attrib['{{{pre}}}noNamespaceSchemaLocation'.format(pre=xsi)] = '..\\xsd_new1\\query.xsd'
            unify_self_signs = etree.SubElement(page, "unify_self_signs")
            unify_self_signs.attrib['action_id'] = '20'
            sender_gln = etree.SubElement(unify_self_signs, "sender_gln")
            sender_gln.text = gln
            unify_date = etree.SubElement(unify_self_signs, "unify_date")
            unify_date.text = now
            unifies = etree.SubElement(unify_self_signs, "unifies")
            for key in d.keys():
                by_gtin = etree.SubElement(unifies, "by_gtin")
                sign_gtin = etree.SubElement(by_gtin, "sign_gtin")
                sign_gtin.text = key
                union = etree.SubElement(by_gtin, "union")
                gs1_sgtin = etree.SubElement(union, "gs1_sgtin")
                gs1_sgtin.text = d.get(key)[1]
                sign_num = etree.SubElement(union, "sign_num")
                sign_num.text = d.get(key)[0]
                product_type = etree.SubElement(union, "product_type")
                product_type.text = str(product_t)
            doc = etree.ElementTree(page)
            doc.write(f"{UPLOAD_FOLDER}/{gln}.xml", pretty_print=True)
            return send_from_directory(UPLOAD_FOLDER,
                                       f'{gln}.xml', as_attachment=True)

    except ValueError as error:
        return render_template('error.html', reason='Неизвестная ошибка, просьба связаться с разработчиком.')


if __name__ == '__main__':
    FormHandler.run(debug=True)

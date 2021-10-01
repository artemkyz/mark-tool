from lxml import etree
from datetime import datetime
import lxml.builder


def document(gln, gtin, kiz, tid, product_t):
    # Генерируем словарь, содержащий gtin с бинарным
    gtin_dct = dict()
    for x in gtin:
        y = bin(int(x[0:9]))[2:].rjust(30, '0')
        z = bin(int(x[9:12]))[2:].rjust(14, '0')
        gtin_dct[x] = y + '0' + z

    # Генерируем словарь из киз и тид и его бинарным представлением
    d = dict(zip(kiz, tid))
    kiz_dct = dict()
    for kiz in d.keys():
        tid = d.get(kiz)
        binary_tid = bin(int(str(tid), 16))[2:]
        if (
                '11100010000000000110100000001010' or '11100010000000000110100000001011' or '11100010100000000110110100010010' or '11100010100000000110110110010010') in binary_tid:
            kiz_dct[kiz] = ['111' + binary_tid[61:95], tid]

    # Объединяем два словаря. В значения словаря gtin добавляем ключ и значения словаря kiz
    d = dict()
    count = 0
    for g in gtin_dct.keys():
        kiz_t = list(kiz_dct.keys())
        # Получаем sgtin96
        c = ['00110000001011' + gtin_dct.get(g) + kiz_dct.get(kiz_t[count])[0], kiz_dct.get(kiz_t[count])[1], kiz_t[count]]
        d[g] = c
        count += 1

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
    for g in d.keys():
        by_gtin = etree.SubElement(unifies, "by_gtin")
        sign_gtin = etree.SubElement(by_gtin, "sign_gtin")
        sign_gtin.text = g
        union = etree.SubElement(by_gtin, "union")
        gs1_sgtin = etree.SubElement(union, "gs1_sgtin")
        gs1_sgtin.text = d.get(g)[0]
        sign_num = etree.SubElement(union, "sign_num")
        sign_num.text = d.get(g)[2]
        sign_tid = etree.SubElement(union, "sign_tid")
        sign_tid.text = d.get(g)[1]
        product_type = etree.SubElement(union, "product_type")
        product_type.text = str(product_t)
    doc = etree.ElementTree(page)
    doc.write(f"uploads/{gln}.xml", pretty_print=True)

from lxml import etree
from datetime import datetime
import lxml.builder
from config import documents_directory
from db_utils import commit_fur


def data_generator(statement, gln):
    data = {}
    for gtin in statement.keys():
        kiz, tid = statement.get(gtin)
        g = gtin_generator(gtin)
        t = tid_to_bin(tid)
        sgtin = '00110000001011' + g + t
        sgtin_hex = hex(int(sgtin, 2))[2:]
        data[gtin] = gln, kiz, tid, sgtin, sgtin_hex

    return data


def gtin_generator(gtin):
    part_1 = bin(int(gtin[0:9]))[2:]
    part_2 = bin(int('0' + gtin[9:12]))[2:]

    return part_1.rjust(30, '0')+part_2.rjust(14, '0')


def tid_to_bin(tid):
    binary_tid = bin(int(tid, 16))[2:]
    if (
            '11100010000000000110100000001010' or '11100010000000000110100000001011' or
            '11100010100000000110110100010010' or '11100010100000000110110110010010') in binary_tid:

        return '111' + binary_tid[61:96]


def document(gln, statement, product_t):
    data = {}
    for gtin in statement.keys():
        kiz, tid = statement.get(gtin)
        g = gtin_generator(gtin)
        t = tid_to_bin(tid)
        sgtin = '00110000001011' + g + t
        sgtin_hex = hex(int(sgtin, 2))[2:]
        data[gtin] = gln, kiz, tid, sgtin, sgtin_hex

    # Формируем документы в формате xml
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
    for g in data.keys():
        by_gtin = etree.SubElement(unifies, "by_gtin")
        sign_gtin = etree.SubElement(by_gtin, "sign_gtin")
        sign_gtin.text = g
        union = etree.SubElement(by_gtin, "union")
        gs1_sgtin = etree.SubElement(union, "gs1_sgtin")
        gs1_sgtin.text = data.get(g)[3]
        sign_num = etree.SubElement(union, "sign_num")
        sign_num.text = data.get(g)[1]
        sign_tid = etree.SubElement(union, "sign_tid")
        sign_tid.text = data.get(g)[2]
        product_type = etree.SubElement(union, "product_type")
        product_type.text = product_t
        # kiz = d.get(g)[2]; tid = d.get(g)[1]; sgtin = d.get(g)[0]; sgtin_hex = hex(int(d.get(g)[0], 2))[2:]
    doc = etree.ElementTree(page)
    doc.write(f"{documents_directory}/{gln}.xml", pretty_print=True)
    commit_fur(data)
    return data

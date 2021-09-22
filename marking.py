import pyexcel
from lxml import etree
import lxml.builder
from datetime import datetime
import csv


class Fur:

    def __init__(self, gtin, tid, kiz):
        self.fur_data = dict(zip(kiz, zip(gtin, tid)))

    def reformat_gtin(self):
        my_dict = {}
        for key in self.fur_data.keys():
            my_dict[key] = [bin(int(str(self.fur_data.get(key)[0])[0:9]))[2:],
                            bin(int(str(self.fur_data.get(key)[0])[9:12]))[2:]]
        return my_dict

    def reformat_tid(self):
        # impinj, nxp_1, nxp_2, alien are chip manufacturers. Each manufacturer has own prefix in serial number.
        # Serial number is stored in user bank memory included in chip.
        impinj = {101: ['11100010100000000001000100000000']}
        nxp_1 = {
            111: ['11100010000000000110100000001010', '11100010000000000110100000001011',
                  '11100010100000000110110100010010', '11100010100000000110110110010010']}
        nxp_2 = {
            111: ['11100010000000000110100000000110', '11100010000000000110100100000110',
                  '11100010000000000110101100000110', '11100010000000000110100000000111',
                  '11100010000000000110100100000111', '11100010000000000110101100000111']}
        alien = {110: ['11100010000000000011010000010100']}

        my_dict = {}
        for key_1 in self.fur_data.keys():
            tid = bin(int(str(self.fur_data.get(key_1)[1]), 16))
            gtin = self.fur_data.get(key_1)[0]

            if tid[2:][:32] in impinj.get(101):
                return "impinj"

            elif tid[2:][:32] in nxp_1.get(111):
                for key in nxp_1.keys():
                    my_dict[key_1] = [gtin, f"{key}{tid[2:][61:]}"]

            elif tid[2:][:32] in nxp_2.get(111):
                for key in nxp_2.keys():
                    my_dict[key_1] = [gtin, f"{key}{tid[2:][21:24]}{tid[2:][32:64]}"]

            elif tid[2:][:32] in alien.get(110):
                for key in alien.keys():
                    my_dict[key_1] = [gtin, f"{key}{tid[2:][61:]}"]
        return my_dict

    def generation_sgtin(self):
        sign_sgtin96 = "00110000"
        sign_sale = "001"
        sign_gtin = "011"
        sign_tid = []
        for tid in self.reformat_tid().values():
            sign_tid.append(tid[1])

        sign_org = []
        sign_prod = []
        for item in self.reformat_gtin().values():
            sign_org.append(item[0])
            sign_prod.append(item[1])

        my_dcit = dict(zip(sign_tid, zip(sign_org, sign_prod)))
        sgtins = []
        for key in my_dcit.keys():
            sgtin = f"{sign_sgtin96}{sign_sale}{sign_gtin}{my_dcit.get(key)[0].rjust(30, '0')}" \
                    f"{my_dcit.get(key)[1].rjust(14, '0')}{key}"
            sgtins.append(sgtin)

        kizs = []
        gtins = []
        tids = []
        for key in self.fur_data.keys():
            kizs.append(key)
            gtins.append(self.fur_data.get(key)[0])
            tids.append(self.fur_data.get(key)[1])
        result = dict(zip(kizs, zip(gtins, tids, sgtins)))

        # with open("output/RFID.csv", "w") as of:
        #     writer = csv.writer(of)
        #     for key, value in result.items():
        #         writer.writerow([key, value[0], str(hex(int(value[2], 2)))[2:]])
        return result


def action20(fur, snd_gln, prod_type):
    if prod_type != '0':
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
        sender_gln.text = snd_gln
        unify_date = etree.SubElement(unify_self_signs, "unify_date")
        unify_date.text = now
        unifies = etree.SubElement(unify_self_signs, "unifies")
        for key in fur.generation_sgtin().keys():
            by_gtin = etree.SubElement(unifies, "by_gtin")
            sign_gtin = etree.SubElement(by_gtin, "sign_gtin")
            sign_gtin.text = str(fur.generation_sgtin().get(key)[0])
            union = etree.SubElement(by_gtin, "union")
            gs1_sgtin = etree.SubElement(union, "gs1_sgtin")
            gs1_sgtin.text = str(fur.generation_sgtin().get(key)[2])
            sign_num = etree.SubElement(union, "sign_num")
            sign_num.text = str(key)
            product_type = etree.SubElement(union, "product_type")
            product_type.text = prod_type
        doc = etree.ElementTree(page)
        doc.write(f"/home/pi/projects/marking/uploads/{snd_gln}/unify_self_signs.xml", pretty_print=True)

    else:
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
        sender_gln.text = snd_gln
        unify_date = etree.SubElement(unify_self_signs, "unify_date")
        unify_date.text = now
        unifies = etree.SubElement(unify_self_signs, "unifies")
        for key in fur.generation_sgtin().keys():
            by_gtin = etree.SubElement(unifies, "by_gtin")
            sign_gtin = etree.SubElement(by_gtin, "sign_gtin")
            sign_gtin.text = str(fur.generation_sgtin().get(key)[0])
            union = etree.SubElement(by_gtin, "union")
            gs1_sgtin = etree.SubElement(union, "gs1_sgtin")
            gs1_sgtin.text = str(fur.generation_sgtin().get(key)[2])
            sign_num = etree.SubElement(union, "sign_num")
            sign_num.text = str(key)
        doc = etree.ElementTree(page)
        doc.write(f"/home/pi/projects/marking/uploads/{snd_gln}/unify_self_signs.xml", pretty_print=True)


def create_report(file):
    file = pyexcel.get_dict(file_name=file)
    tid_list = file.get("TID / SGTIN")
    gtin_list = file.get("Продукция")
    kiz_list = file.get("Номер КиЗ")
    fur = Fur(gtin=gtin_list, tid=tid_list, kiz=kiz_list)
    return fur

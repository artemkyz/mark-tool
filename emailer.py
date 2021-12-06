import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send_mail(send_from, send_to, subject, text, files=None,
              server="127.0.0.1:25"):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


def send_registration(admin_email, email, domain_name, token):
    send_mail(send_from=admin_email, send_to=[email], subject='Регистрация Маркировка',
              text=f'Для подтверждения регистрации на сайте mark-tool перейдите по ссылке https://{domain_name}/'
                   f'confirm_registration?token={token} '
                   f'В случае если это письмо ошибочно попало в Ваш почтовый ящик просто удалите его.')


def send_document(admin_email, email,documents_directory, gln):
    send_mail(send_from=admin_email, send_to=[email], subject='Маркировка',
              text='во вложении документ для маркировки шуб', files=[f'{documents_directory}/{gln}.xml'])


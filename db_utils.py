import sqlite3
from config import dbase


def commit_new_user(date, gln, password, email):
    connector = sqlite3.connect(dbase)
    cursor = connector.cursor()
    cursor.execute('''INSERT INTO users VALUES(?, ?, ?, ?)''', (date, gln, password, email))
    connector.commit()
    connector.close()
    print('SERVICE: commit user in base success')


def commit_temp_user(date, gln, password, email, token):
    connector = sqlite3.connect(dbase)
    cursor = connector.cursor()
    cursor.execute('''INSERT INTO temp_users VALUES(?, ?, ?, ?, ?)''', (date, gln, password, email, token))
    connector.commit()
    connector.close()
    print('SERVICE: commit user in base success')


def check_user_token(token):
    connector = sqlite3.connect(dbase)
    cursor = connector.cursor()
    cursor.execute('''SELECT * from temp_users WHERE token=?''', (token, ))
    data = cursor.fetchone()
    if not data:
        connector.close()
        return False
    connector.close()
    return data


def delete_temp_user(gln):
    connector = sqlite3.connect(dbase)
    cursor = connector.cursor()
    cursor.execute('''DELETE from temp_users WHERE gln=?''', (gln, ))
    connector.commit()
    connector.close()
    print(f'{gln} deleted from temp_users')


def new_base():
    connector = sqlite3.connect(dbase)
    cursor = connector.cursor()
    cursor.execute('''CREATE TABLE users (date text NOT NULL, gln text NOT NULL UNIQUE,  
                    password text NOT NULL, email text NOT NULL UNIQUE)''')

    cursor.execute('''CREATE TABLE temp_users (date text NOT NULL, gln text NOT NULL UNIQUE,  
                    password text NOT NULL, email text NOT NULL UNIQUE, token text NOT NULL UNIQUE)''')

    cursor.execute('''CREATE TABLE furs (gln text, gtin text, kiz text, tid text, sgtin text, sgtin_hex text,
                    FOREIGN KEY(gln) REFERENCES users(gln))''')
    connector.commit()
    connector.close()
    print('SERVICE: new base was created')


def check_user_credentials(gln, password):
    connector = sqlite3.connect(dbase)
    cursor = connector.cursor()
    cursor.execute('''SELECT gln from users WHERE gln=? AND password=?''', (gln, password))
    if not cursor.fetchone():
        connector.close()
        return False
    connector.close()
    return True


def check_user_exist(gln):
    connector = sqlite3.connect(dbase)
    cursor = connector.cursor()
    cursor.execute('''SELECT gln from users WHERE gln=?''', (gln, ))
    if not cursor.fetchone():
        connector.close()
        return False
    connector.close()
    return True


def commit_fur(data):
    connector = sqlite3.connect(dbase)
    cursor = connector.cursor()
    for g in data.keys():
        cursor.execute('''INSERT INTO furs VALUES(?, ?, ?, ?, ?, ?)''',
                       (data.get(g)[0], g, data.get(g)[1], data.get(g)[2], data.get(g)[3], data.get(g)[4]))
    connector.commit()
    connector.close()
    print('SERVICE: commit furs in base success')


def marked_furs(gln):
    connector = sqlite3.connect(dbase)
    cursor = connector.cursor()
    cursor.execute('''SELECT * from furs WHERE gln=?''', (gln, ))
    data = cursor.fetchall()
    if not data:
        connector.close()
        return False
    return data

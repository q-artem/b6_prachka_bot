import random
import sqlite3

from aiogram import types

bd = sqlite3.connect("users.sqlite")  # подключение к бд


async def get_value_from_id(idq, table="users", sign_column="id", fields="*", get_all=False, fetchone=True):
    debug_mess = ""
    try:  # получение значения из базы
        if not get_all:
            debug_mess = """SELECT {fields} FROM {table} WHERE {sign_column} = {idq}""".format(fields=fields,
                                                                                               table=table,
                                                                                               sign_column=sign_column,
                                                                                               idq=idq, )
            data = bd.cursor().execute(
                """SELECT {fields} FROM {table} WHERE {sign_column} = ?""".format(fields=fields,
                                                                                  table=table,
                                                                                  sign_column=sign_column, ),
                (idq,))
            if fetchone:
                data = data.fetchone()
            else:
                data = data.fetchall()
        else:
            debug_mess = f'''SELECT {fields} FROM {table} >>> '''
            data = bd.cursor().execute('''SELECT {fields} FROM {table}'''.format(fields=fields,
                                                                                 table=table,
                                                                                 )).fetchall()
        if fields != "*" and len(fields.split(",")) == 1 and (not get_all):
            if data is None:
                print(debug_mess + " >>> " + "None")
                return None
            print(debug_mess + " >>> " + str(data[0]))
            return data[0]
        else:
            print(debug_mess + " >>> " + str(data))
            return data
    except BaseException as e:
        print("In", "getValueFromId", str(e) + "; request: " + debug_mess)
        return False


async def enter_bd_request(rq: str):
    try:
        data = bd.cursor().execute(rq).fetchall()
        bd.commit()
        print("User bd request: " + rq + " >>> " + str(data))
        return True, data
    except BaseException as e:
        print("In", "getValueFromId", e)
        return False, e


async def write_value_from_id(idq, fields, value, table="users"):  # изменение значения в базе
    try:
        data = bd.cursor().execute("""UPDATE {table} SET {fields} = ? WHERE id = ?""".format(table=table,
                                                                                             fields=fields,
                                                                                             ), (value, idq)).fetchone()
        bd.commit()
        print("""UPDATE {table} SET {fields} = {value} WHERE id = {idq}""".format(table=table,
                                                                                  fields=fields,
                                                                                  value=value,
                                                                                  idq=idq))
        return data
    except BaseException as e:
        print("In", "writeValueFromId", e)
        return False


async def add_user(idq, tb="users") -> bool:  # добавление пользователя в базу данных
    try:
        bd.cursor().execute(f"""INSERT INTO {tb} (id) VALUES (?)""", (idq,))
        bd.commit()
    except sqlite3.Error as e:
        print("Ошибка записи в БД:", e)
        return False
    print("Добавлен новый пользователь, запись в БД завершена")
    return True

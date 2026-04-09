import sqlite3


def create_db():
    connect = sqlite3.connect("data/data.db")
    q = connect.cursor()
    q.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER,
        balance REAL,
        count INTEGER,
        date TEXT,
        ban INTEGER
    )""")
    q.execute("""CREATE TABLE IF NOT EXISTS admin_settings(
        p2p TEXT,
        samples INTEGER
    )""")
    q.execute("""CREATE TABLE IF NOT EXISTS busket_info(
        id INTEGER,
        staff_id TEXT,
        summa INTEGER,
        staff TEXT,
        city TEXT,
        date TEXT

    )""")
    connect.commit()
    return True


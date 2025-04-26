import sqlite3

dtb = "data/database/petme.db"

def create_database():
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS client (
                        id_client INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL,
                        password TEXT NOT NULL,
                        fullname TEXT,
                        city TEXT,
                        state TEXT,
                        country TEXT,
                        phone TEXT
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS coordinator (
                        id_coordinator INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL,
                        password TEXT NOT NULL,
                        branch TEXT NOT NULL,
                        fullname TEXT,
                        city TEXT,
                        state TEXT,
                        country TEXT,
                        phone TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS pet (
                        id_pet INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL,
                        breed TEXT NOT NULL,
                        gender TEXT NOT NULL,
                        color TEXT NOT NULL,
                        name TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        branch TEXT NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS adopt (
                        id_adopt INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        pet_id INTEGER,
                        date DATE NOT NULL,
                        note TEXT,
                        status INTEGER NOT NULL,
                        approve_id INTEGER,
                        FOREIGN KEY(pet_id) REFERENCES pet(id_pet),
                        FOREIGN KEY(user_id) REFERENCES users(id_user),
                        FOREIGN KEY(approve_id) REFERENCES approval(id_approve)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS approval (
                        id_approve INTEGER PRIMARY KEY AUTOINCREMENT,
                        coordinator_id INTEGER,
                        adopt_id INTEGER,
                        approve INTEGER NOT NULL,
                        note TEXT NOT NULL,
                        date DATE NOT NULL,
                        FOREIGN KEY(coordinator_id) REFERENCES coordinator(id_coordinator),
                        FOREIGN KEY(adopt_id) REFERENCES adopt(id_adopt)
                    )''')

    conn.commit()
    conn.close()

create_database()
import sqlite3
from functions.database import dtb

def check_email(email):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM coordinator WHERE email = ?', 
                   (email,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('SELECT email FROM client WHERE email = ?', 
                   (email,))
        result = cursor.fetchone()

    conn.close()
    return result[0] if result else None

def check_pass(email):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM coordinator WHERE email = ?', 
                   (email,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute('SELECT password FROM client WHERE email = ?', 
                    (email,))
        result = cursor.fetchone()

    conn.close()
    return result[0] if result else None

def register(email, password):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO client (email, password) VALUES (?, ?)',
                   (email, password))
    conn.commit()
    conn.close()

def get_user_id(email):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('SELECT id_coordinator FROM coordinator WHERE email = ?', 
                   (email,))
    result = cursor.fetchone()
    role = "coordinator"
    if result is None:
        cursor.execute('SELECT id_client FROM client WHERE email = ?', 
                   (email,))
        result = cursor.fetchone()
        role = "client"
    conn.close()
    return result[0], role if result else None

def add_coordinator(email, password, branch):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO coordinator (email, password, branch) VALUES (?, ?, ?)',
                   (email, password, branch))
    conn.commit()
    conn.close()
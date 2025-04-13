import sqlite3
from functions.database import dtb

def check_email(email):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM client WHERE email = ?', 
                   (email,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0] if result else None

def check_pass(email):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM client WHERE email = ?', 
                   (email,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0] if result else None

def register(email, password):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO client (email, password) VALUES (?, ?)',
                   (email, password))
    conn.commit()
    conn.close()

def get_client_id(email):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('SELECT id_client FROM client WHERE email = ?', 
                   (email,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0] if result else None

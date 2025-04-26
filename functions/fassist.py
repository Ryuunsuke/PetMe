import sqlite3
from datetime import datetime
from functions.database import dtb

def donate_pet(type, breed, gender, color, name, age, branch):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = 'INSERT INTO pet (type, breed, gender, color, name, age, branch) VALUES (?, ?, ?, ?, ?, ?, ?)'
    cursor.execute(query, (type, breed, gender, color, name, age, branch))
    conn.commit()
    print("Pet inserted successfully.")
    conn.close()
    return "Pet is now in the database."

def check_adopt_status(name):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = 'SELECT status FROM adopt WHERE name = ?'
    cursor.execute(query, (name,))
    conn.commit()
    status = cursor.fetchone()
    conn.close()
    return status[0]

def check_exist_adopt(name):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = 'SELECT id_adopt FROM adopt WHERE name = ?'
    cursor.execute(query, (name,))
    exist = cursor.fetchone()
    conn.close()
    return 1 if exist else 0
        
def adopt(user_id, name, note):
    check = check_exist_adopt(name)
    if check == 1:
        return F"{name} has already been/being adopted by someone else."
    pet_id = get_pet_id(name)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = 'INSERT INTO adopt (user_id, pet_id, date, note, approved) VALUES (?, ?, ?, ?, ?)'
    cursor.execute(query, (user_id, pet_id, date, note, 0))
    conn.commit()
    conn.close()
    return "Pet is now waiting for approval"

def approve(coordinator_id, name, approve, note):
    adopt_id = get_pet_id_from_adopt(name)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = 'INSERT INTO approval (coordinator_id, adopt_id, approve, note, date) VALUES (?, ?, ?, ?, ?)'
    cursor.execute(query, (coordinator_id, adopt_id, approve, note, date))
    conn.commit()
    if approve == 0:
        print("Pet adoption is not approved")
    else:
        print("Pet is approvedl")
    conn.close()

def disapprove_reason(name):
    adopt_id = get_pet_id_from_adopt(name)
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = 'SELECT note FROM adopt WHERE adopt_id = ?'
    cursor.execute(query, (adopt_id,))
    reason = cursor.fetchone()
    conn.close()
    return reason[0] if reason else None

def get_pet_id(name):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = 'SELECT id_pet FROM pet WHERE name = ?'
    cursor.execute(query, (name,))
    id = cursor.fetchone()
    conn.close()
    return id[0]

def get_pet_id_from_adopt(name):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = 'SELECT pet_id FROM adopt WHERE name = ?'
    cursor.execute(query, (name,))
    id = cursor.fetchone()
    conn.close()
    return id[0]

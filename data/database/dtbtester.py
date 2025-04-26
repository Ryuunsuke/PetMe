import sqlite3

dtb = "data/database/petme.db"

def select():
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    
    # Be careful! Only use this if `tablee` is a trusted input.
    query = f'SELECT * FROM pet'
    cursor.execute(query)
    result = cursor.fetchall()
    for results in result:
        print(results)
    conn.close()

select()

def add_coordinator(email, password, branch):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO coordinator (email, password, branch) VALUES (?, ?, ?)',
                   (email, password, branch))
    conn.commit()
    conn.close()

add_coordinator("co@co.co", "co", "Kashmir")
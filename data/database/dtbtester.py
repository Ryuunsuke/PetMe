import sqlite3
from datetime import datetime

dtb = "data/database/petme.db" 

def select():
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    
    # Be careful! Only use this if `tablee` is a trusted input.
    query = f'SELECT * FROM approval'
    cursor.execute(query)
    result = cursor.fetchall()
    for results in result:
        print(results)
    conn.close()

def select2():
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    
    # Be careful! Only use this if `tablee` is a trusted input.
    query = f'SELECT * FROM adopt'
    cursor.execute(query)
    result = cursor.fetchall()
    for results in result:
        print(results)
    conn.close()

# select()

def add_coordinator(email, password, branch):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO coordinator (email, password, branch) VALUES (?, ?, ?)',
                   (email, password, branch))
    conn.commit()
    conn.close()

#Insert pet into the database for adoption
def donate_pet(type, breed, gender, color, name, age, branch):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = 'INSERT INTO pet (type, breed, gender, color, name, age, branch) VALUES (?, ?, ?, ?, ?, ?, ?)'
    cursor.execute(query, (type, breed, gender, color, name, age, branch))
    conn.commit()
    print("Pet inserted successfully.")
    conn.close()
    return "Pet is now in the database."

#Check whether adoption has already been/being made by someone else
def check_exist_adopt(name):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    pet_id = get_pet_id(cursor, name)
    query = 'SELECT id_adopt FROM adopt WHERE pet_id = ?'
    cursor.execute(query, (pet_id,))
    exist = cursor.fetchone()
    conn.close()
    return 1 if exist else 0
        
#Registering adoption for current user for specified pet
def adopt(user_id, name, note):
    check = check_exist_adopt(name)
    if check == 1:
        return F"{name} has already been/being adopted by someone else."
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    pet_id = get_pet_id(cursor, name)
    query = 'INSERT INTO adopt (user_id, pet_id, date, note, status) VALUES (?, ?, ?, ?, ?)'
    cursor.execute(query, (user_id, pet_id, date, note, 0))
    conn.commit()
    conn.close()
    return "Pet is now waiting for approval"

#(Client only) making the output easier for client to understand for adoption status
def check_adoption_status_for_client(name):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = '''
        SELECT adopt.status
        FROM adopt
        JOIN pet ON adopt.pet_id = pet.id_pet
        WHERE pet.name = ?
    '''
    cursor.execute(query, (name,))
    status = cursor.fetchone()
    conn.close()
    status = status[0]
    if status == -1:
        return "Pet adoption is rejected."
    elif status == 0:
        return "Pet adoption is still waiting for a coordinator to approve."
    elif status == 1:
        return "Pet adoption is approved."
    else:
        return f"Adoption procedure hasn't been made on {name}"

#(Coordinator only) approve an adoption made by client
def approve(coordinator_id, name, approve, note):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    adopt_id = get_adopt_id(cursor, name)
    query = 'INSERT INTO approval (coordinator_id, adopt_id, approve, note, date) VALUES (?, ?, ?, ?, ?)'
    cursor.execute(query, (coordinator_id, adopt_id, int(approve), note, date))
    update_status(cursor, approve, note ,adopt_id)
    conn.commit()
    conn.close()
    if approve == -1:
        return f"{name}'s adoption is rejected on {date}"
    else:
        return f"{name}'s adoption is approved on {date}"
    
#Get the reason why the approval/rejection was made 
def status_reason(name):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    adopt_id = get_adopt_id(cursor, name)
    query = 'SELECT note FROM adopt WHERE id_adopt = ?'
    cursor.execute(query, (adopt_id,))
    reason = cursor.fetchone()
    conn.close()
    return reason[0] if reason else "No reason specified"

#Self-explanatory
def get_pet_id(cursor, name):
    query = 'SELECT id_pet FROM pet WHERE name = ?'
    cursor.execute(query, (name,))
    id = cursor.fetchone()
    return id[0]

#Self-explanatory
def get_adopt_id(cursor, name):
    pet_id = get_pet_id(cursor, name)
    query = 'SELECT id_adopt FROM adopt WHERE pet_id = ?'
    cursor.execute(query, (pet_id,))
    adopt_id = cursor.fetchone()
    return adopt_id[0]

#(Client only) Check whether user has made an adoption
def check_user_existing_adopt(user_id):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = '''
        SELECT pet.name
        FROM adopt
        JOIN pet ON adopt.pet_id = pet.id_pet
        WHERE adopt.user_id = ?
    '''
    cursor.execute(query, (user_id,))
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    if names:
        return names
    else:
        return "You currently have no adoption."
    
#(Coordinator only) Check for all the approvals from current coordinator
def check_coordinator_approvals(user_id):
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = '''
        SELECT pet.name
        FROM adopt
        JOIN pet ON adopt.pet_id = pet.id_pet
        JOIN approval ON approval.adopt_id = adopt.id_adopt
        WHERE approval.coordinator_id = ?
    '''
    cursor.execute(query, (user_id,))
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    if names:
        return names
    else:
        return "You currently have no approvals."

#Updating status in adopt as the coordinator make changes to approval    
def update_status(cursor, approve, note, adopt_id):
    query = '''
        UPDATE adopt
        SET status = ?, note = ?
        WHERE id_adopt = ?
    '''
    cursor.execute(query, (approve, note, adopt_id))

#(Coordinator only) Make changes to existing status
def modify_status(user_id, name, approve, note):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    adopt_id = get_adopt_id(cursor, name)
    query = '''
        UPDATE approval
        SET approve = ?, note = ?, date = ?
        WHERE coordinator_id = ? AND adopt_id = ?
    '''
    cursor.execute(query, (approve, note, date, user_id, adopt_id))
    update_status(cursor, approve, note, adopt_id)
    conn.commit()
    conn.close()
    if approve == -1:
        return f"{name}'s adoption status has been modified to rejected on {date}"
    else:
        return f"{name}'s adoption status has been modified to approved on {date}"
    
def deletedata():
    conn = sqlite3.connect(dtb)
    cursor = conn.cursor()
    query = '''
        DELETE FROM adopt
    '''
    cursor.execute(query)
    query = '''
        DELETE FROM sqlite_sequence WHERE name='adopt';
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()
    
# adopt(1, "Russia", "")
# adopt(1, "Bongo", "")
# adopt(1, "Lucy", "")

#check_adoption_status_for_client("Russia")
# approve(1, "Russia", -1, "Not enough documents.")
# approve(1, "Bongo", 1, "Verified documents.")
#modify_status(1, "Russia", -1, "Unverified documents.")
#check_user_existing_adopt(1)
output = status_reason("Russia")
# output = check_coordinator_approvals(1)
print(output)
# deletedata()
select()
select2()
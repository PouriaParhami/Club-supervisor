import sqlite3
from datetime import datetime


def memebrs_table():
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        members_id INTEGER PRIMARY KEY,
        e_first_name TEXT,
        e_last_name TEXT,
        f_first_name TEXT,
        f_last_name TEXT
    )
    ''')
    conn.commit()
    conn.close()

def entrance_table():
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entrance_records (
        ent_id INTEGER PRIMARY KEY,
        members_id, 
        date TEXT,
        time TEXT,
        jalali_date TEXT,
        photo_path TEXT,
        FOREIGN KEY (members_id) REFERENCES members(members_id)
    )
    ''')
    conn.commit()
    conn.close()

def setup_database():
    memebrs_table()
    entrance_table()
     
def read_data():
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM entrance_records')
    records = cursor.fetchall()
    
    conn.close()
    return records 

def delete_all_records():
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM entrance_records')
    conn.commit()
    
    conn.close()

def save_record_to_db(member_name, date, time, jalali_date, photo_path):
    print(member_name, date, time, jalali_date, photo_path)
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()
    
    fist_name, last_name = member_name.split("_")
    
    cursor.execute('''
                   SELECT rowid 
                   FROM members 
                   WHERE e_first_name = (?) AND e_last_name = (?)
                   ''', (fist_name, last_name))
    
    member_id = cursor.fetchall()[0][0]
    print(member_id)

    cursor.execute('''
    INSERT INTO entrance_records (members_id, date, time, jalali_date, photo_path)
    VALUES (?, ?, ?, ?, ?)
    ''', (member_id, date, time, jalali_date, photo_path))

    conn.commit()
    conn.close()
    
def load_recognized_today():
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()

    today_date = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
    SELECT m.e_first_name, m.e_last_name, m.f_first_name, m.f_last_name 
    FROM entrance_records er
    JOIN members m ON er.members_id = m.members_id
    WHERE date = ?
    ''', (today_date,))

    records = cursor.fetchall()
    
    conn.close()

    return {(record[0] + "_" + record[1], today_date) for record in records}

def exoprt_all()  :
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()

    today_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
    SELECT m.e_first_name, m.e_last_name, m.f_first_name, m.f_last_name, er.date, er.time, er.jalali_date
    FROM entrance_records er
    JOIN members m ON er.members_id = m.members_id
    WHERE er.date = ?
    ''', (today_date,))
    
    records = cursor.fetchall()
    conn.close()

    return {(record) for record in records}

def export_all_data():
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT m.e_first_name, m.e_last_name, m.f_first_name, m.f_last_name, er.date, er.time, er.jalali_date
    FROM entrance_records er
    JOIN members m ON er.members_id = m.members_id
    ''')

    records = cursor.fetchall()
    conn.close()
    
    return records

def select_all_memebrs():
    conn = sqlite3.connect('club_members.db')
    
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM members')
    records = cursor.fetchall()
    
    conn.close()
    return records
     
def get_detailed_entrance_records():
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()

    today_date = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
    SELECT m.e_first_name, m.e_last_name, m.f_first_name, m.f_last_name, er.date, er.time, er.jalali_date
    FROM entrance_records er
    JOIN members m ON er.members_id = m.members_id
    WHERE er.date = ?
    ''', (today_date,))

    records = cursor.fetchall()
    conn.close()

    return records

def add_member(e_first_name, e_last_name, f_first_name, f_last_name):
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO members (e_first_name, e_last_name, f_first_name, f_last_name)
    VALUES (?, ?, ?, ?)
    ''', (e_first_name, e_last_name, f_first_name, f_last_name))

    conn.commit()
    conn.close()
     
def edit_memebrs(new_e_first_name, new_e_last_name, new_f_first_name, new_f_last_name, memebr_id):
    conn = sqlite3.connect('club_members.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE members 
        SET e_first_name = ?, e_last_name = ?, f_first_name = ?, f_last_name = ?
        WHERE members_id = ?
    ''', (new_e_first_name, new_e_last_name, new_f_first_name, new_f_last_name, memebr_id))

    conn.commit()
    conn.close()
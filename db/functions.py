import mysql.connector
import os
from uuid import uuid4
from . import *

rooms_tablename = f"{db_name}.rooms"
applications_tablename = f"{db_name}.applications"

db = mysql.connector.connect(host=db_host, port=db_port, user=db_username, password=db_password, database=db_name)

def get_room_row(room_id):
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {rooms_tablename} WHERE room_id = {room_id}")
    res = cur.fetchone()
    print("get_room_row", res)
    db.commit()
    cur.close()
    return res

def get_rooms():
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {rooms_tablename}")
    res = cur.fetchall()
    print("get_rooms", res)
    db.commit()
    cur.close()
    return res

def get_applications():
    cur = db.cursor()
    cur.execute(f"SELECT * FROM {applications_tablename}")
    res = cur.fetchall()
    print("get_applications", res)
    db.commit()
    cur.close()
    return res

def new_application(room_id: int, months: int):
    cur = db.cursor()
    cur.execute(f"INSERT INTO {applications_tablename}(application_id, status, months, room_id) VALUES ('{str(uuid4())}', 'pending', {months}, {room_id})")
    print("new_application")
    db.commit()
    cur.close()

def cancel_application(application_id):
    cur = db.cursor()
    cur.execute(f"UPDATE {applications_tablename} SET status = 'cancelled' WHERE application_id = '{application_id}'")
    print("cancel_application")
    db.commit()
    cur.close()
from django.shortcuts import render

import mysql.connector

def index(request):
    conn = mysql.connector.connect(
    host="127.0.0.1",
    database = "bills",
    user="webapp",
    password="123456")   
    
    try:
        cursor = conn.cursor()
        cursor.execute("select * from bills")

        rows = cursor.fetchall()
      
    finally:
        conn.close()

    return render(request,'bill_data/table.html', {'obj': rows})
    



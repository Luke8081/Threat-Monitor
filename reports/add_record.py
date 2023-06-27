import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

sql = f'''INSERT INTO alert_Summary('Address','Low_Alert', 'Medium_Alert', 'High_Alert', 'Date')
            VALUES(?,?,?,?,?)'''

params = ("test_address", 0, 5, 1, '2023-06-08')

cursor.execute(sql, params)

conn.commit()
conn.close()

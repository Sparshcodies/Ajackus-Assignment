import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM Employees")
print("Employees Table:")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT * FROM Departments")
print("\nDepartments Table:")
for row in cursor.fetchall():
    print(row)

conn.close()

import sqlite3
import csv

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")

# Create Departments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Departments (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL UNIQUE,
    Manager TEXT NOT NULL
);
""")

# Create Employees table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Employees (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Department_ID INTEGER NOT NULL,
    Salary INTEGER NOT NULL,
    Hire_Date TEXT NOT NULL,
    FOREIGN KEY (Department_ID) REFERENCES Departments(ID) ON DELETE CASCADE
);
""")

# Insert data into Departments table
with open("departments.csv", "r") as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    for row in csv_reader:
        cursor.execute("INSERT INTO Departments (ID, Name, Manager) VALUES (?, ?, ?)", row)

# Insert data into Employees table
with open("employees.csv", "r") as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    for row in csv_reader:
        employee_id, employee_name, department_name, salary, hire_date = row
        cursor.execute("SELECT ID FROM Departments WHERE Name = ?", (department_name,))
        department_id_result = cursor.fetchone()

        if department_id_result:  
            department_id = department_id_result[0]
            cursor.execute("INSERT INTO Employees (ID, Name, Department_ID, Salary, Hire_Date) VALUES (?, ?, ?, ?, ?)",(employee_id, employee_name, department_id, salary, hire_date))
        else:
            print(f"⚠ Warning: Department '{department_name}' not found for Employee '{employee_name}'")

conn.commit()
conn.close()

print("Database and tables created successfully!")

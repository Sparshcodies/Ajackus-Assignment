import sqlite3
import csv

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Employees (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Department TEXT NOT NULL,
    Salary INTEGER NOT NULL,
    Hire_Date TEXT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Departments (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Manager TEXT NOT NULL
);
""")

# Insert data into Employees table from CSV
with open("employees.csv", "r") as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip header row
    for row in csv_reader:
        cursor.execute("INSERT INTO Employees (ID, Name, Department, Salary, Hire_Date) VALUES (?, ?, ?, ?, ?)", row)

with open("departments.csv", "r") as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip header row
    for row in csv_reader:
        cursor.execute("INSERT INTO Departments (ID, Name, Manager) VALUES (?, ?, ?)", row)
        
conn.commit()
conn.close()

print("Database and tables created successfully!")

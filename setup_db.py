import sqlite3

def initialize_database():
    conn = sqlite3.connect('shakeshack.db')
    cursor = conn.cursor()

    # Create the category tables

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Burgers (
            name TEXT NOT NULL,
            price REAL NOT NULL,
            calories INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Chicken (
            name TEXT NOT NULL,
            price REAL NOT NULL,
            calories INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Fries (
            name TEXT NOT NULL,
            price REAL NOT NULL,
            calories INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Milkshakes (
            name TEXT NOT NULL,
            price REAL NOT NULL,
            calories INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Drinks (
            name TEXT NOT NULL,
            price REAL NOT NULL,
            calories INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized")

if __name__ == "__main__":
    initialize_database()
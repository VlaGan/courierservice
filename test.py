import sqlite3


global db
global sql
db = sqlite3.connect('base.db', check_same_thread=False)
sql = db.cursor()


print("USERS:")
for i in sql.execute(f"SELECT * FROM users"):
    print("   ",i)

sql.execute(f"DROP TABLE users")
db.commit()

sql.execute(f"DROP TABLE orders")
db.commit()
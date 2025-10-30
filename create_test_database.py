import sqlite3, os

db_path = "sample.db"
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""CREATE TABLE users(
    uid TEXT PRIMARY KEY,
    pwd TEXT,
    role TEXT CHECK(role IN ('customer', 'sales'))
)""")

c.execute("""CREATE TABLE customers(
    cid INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
)""")

c.execute("""CREATE TABLE products(
    pid INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL,
    stock_count INTEGER,
    descr TEXT
)""")

c.execute("""CREATE TABLE orders(
    ono INTEGER PRIMARY KEY,
    cid INTEGER,
    sessionNo INTEGER,
    odate TEXT,
    shipping_address TEXT,
    FOREIGN KEY(cid) REFERENCES customers(cid)
)""")

c.execute("""CREATE TABLE orderlines(
    ono INTEGER,
    lineNo INTEGER,
    pid INTEGER,
    qty INTEGER,
    uprice REAL,
    PRIMARY KEY(ono, lineNo),
    FOREIGN KEY(ono) REFERENCES orders(ono),
    FOREIGN KEY(pid) REFERENCES products(pid)
)""")

c.execute("""CREATE TABLE sessions(
    cid INTEGER,
    sessionNo INTEGER,
    start_time TEXT,
    end_time TEXT,
    PRIMARY KEY(cid, sessionNo),
    FOREIGN KEY(cid) REFERENCES customers(cid)
)""")

c.execute("""CREATE TABLE viewedProduct(
    cid INTEGER,
    sessionNo INTEGER,
    ts TEXT,
    pid INTEGER
)""")

c.execute("""CREATE TABLE search(
    cid INTEGER,
    sessionNo INTEGER,
    ts TEXT,
    query TEXT
)""")

c.execute("""CREATE TABLE cart(
    cid INTEGER,
    sessionNo INTEGER,
    pid INTEGER,
    qty INTEGER
)""")

c.executemany("INSERT INTO users VALUES(?,?,?)", [
    ("u1","pass123","customer"),
    ("u2","secret","sales")
])

c.executemany("INSERT INTO customers VALUES(?,?,?)", [
    (1,"Alice Smith","alice@example.com"),
    (2,"Bob Johnson","bob@example.com"),
    (3,"William Shakespeare","literary@example.com"),
    (4,"Franz Kafka","metamorphosis@example.com")
])

c.executemany("INSERT INTO products VALUES(?,?,?,?,?,?)", [
    (101,"Laptop","Electronics",1200.00,5,"High performance laptop"),
    (102,"Headphones","Electronics",150.00,20,"Noise-cancelling"),
    (103,"Coffee Maker","Home",80.00,10,"12-cup maker"),
    (104, "Laptop", "Electric", 1300.00, 6, "Lap laps"),
    (105,"Calculator","Electric",15.00,10,"Casio")
])

c.executemany("INSERT INTO sessions VALUES(?,?,?,?)", [
    (1,1,"2025-09-01 10:00","2025-09-01 10:30"),
    (1,2,"2025-09-05 09:00","2025-09-05 09:10"),
    (2,1,"2025-09-05 11:00","2025-09-05 11:40")
])

c.executemany("INSERT INTO viewedProduct VALUES(?,?,?,?)", [
    (1,1,"2025-09-01 10:05",101),
    (1,1,"2025-09-01 10:10",102),
    (2,1,"2025-09-05 11:10",103),
    (2,1,"2025-09-19 10:09",103),
    (1,2,"2012-09-12 10:03",102),
    (3,1,"1243-09-32 09:21",101),
    (3,2,"2025-10-09 01:23",101),
    (4,1,"2025-09-09 12:02",105),
    (4,1,"2025-09-09 12:02",104),
    (4,1,"2025-09-09 12:02",104),
    (4,1,"2025-09-09 12:02",101),
    (4,1,"2025-09-09 12:02",104)
])

c.executemany("INSERT INTO search VALUES(?,?,?,?)", [
    (1,1,"2025-09-01 10:06","laptop"),
    (2,1,"2025-09-05 11:15","coffee")
])

c.executemany("INSERT INTO cart VALUES(?,?,?,?)", [
    (1,1,101,1),
    (1,2,102,2),
    (2,1,103,1)
])

c.executemany("INSERT INTO orders VALUES(?,?,?,?,?)", [
    (9001,1,1,"2025-09-01","123 Main St Edmonton"),
    (9002,2,1,"2025-10-25","456 Pine Ave Calgary"),
    (9003,2,2,"2025-10-23","456 Pine Ave Calgary"),
    (9004,4,1,"2025-10-30","Golden Brick Road California"),
    (9005,3,1,"2025-10-29","12 buckle my shoes St Edmonton")
])

c.executemany("INSERT INTO orderlines VALUES(?,?,?,?,?)", [
    (9001,1,101,1,1200.00),
    (9001,2,102,1,150.00),
    (9002,1,103,2,80.00),
    (9001,3,103,5,80.00),
    (9003,1,101,2,150.00),
    (9001,4,101,2,1200.00),
    (9004,4,101,4,150.00),
    (9005,1,101,4,150.00),
    (9005,2,104,3,10.00),
    (9004,2,103,1,150.00),
    (9004,1,104,1,10.00),
    (9004,3,102,3,80.00)
])

conn.commit()
conn.close()

db_path

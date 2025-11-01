import sqlite3, os

db_path = "sample.db"
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Schema
c.execute("""CREATE TABLE users(uid TEXT PRIMARY KEY, pwd TEXT, role TEXT CHECK(role IN ('customer','sales')));""")
c.execute("""CREATE TABLE customers(cid INTEGER PRIMARY KEY, name TEXT, email TEXT);""")
c.execute("""CREATE TABLE products(pid INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, stock_count INTEGER, descr TEXT);""")
c.execute("""CREATE TABLE orders(ono INTEGER PRIMARY KEY, cid INTEGER, sessionNo INTEGER, odate TEXT, shipping_address TEXT);""")
c.execute("""CREATE TABLE orderlines(ono INTEGER, lineNo INTEGER, pid INTEGER, qty INTEGER, uprice REAL, PRIMARY KEY(ono,lineNo));""")
c.execute("""CREATE TABLE sessions(cid INTEGER, sessionNo INTEGER, start_time TEXT, end_time TEXT, PRIMARY KEY(cid,sessionNo));""")
c.execute("""CREATE TABLE viewedProduct(cid INTEGER, sessionNo INTEGER, ts TEXT, pid INTEGER);""")
c.execute("""CREATE TABLE search(cid, sessionNo, ts, query);""")
c.execute("""CREATE TABLE cart(cid, sessionNo, pid, qty);""")

# Base data
c.executemany("INSERT INTO users VALUES(?,?,?)",[
("1","pass123","customer"),("2","secret","sales"),("3","1234","customer")
])

c.executemany("INSERT INTO customers VALUES(?,?,?)",[
(1,"Alice Smith","alice@example.com"),
(2,"Bob Johnson","bob@example.com"),
(3,"Carol Jones",None)
])

# Core products
products = [
(101,"Laptop","Electronics",1200.00,5,"High performance work laptop"),
(102,"Headphones","Electronics",150.00,20,"Noise-cancelling over-ear"),
(103,"Coffee Maker","Home",80.00,10,"12-cup brewing system"),
(104,"Deluxe Coffee Brewer","Home",95.00,7,"12-cup brewing system"),
(105,"USB Cable","Accessories",10.00,-3,"Should not have negative stock")
]

# Additional ~50 products
more_products = [
(106,"Wireless Mouse","Electronics",25.00,50,"2.4GHz optical mouse"),
(107,"Mechanical Keyboard","Electronics",90.00,15,"RGB backlit keys"),
(108,"Bluetooth Speaker","Electronics",45.00,30,"Portable mini speaker"),
(109,"Smartphone Stand","Accessories",12.00,100,"Adjustable angle"),
(110,"LED Desk Lamp","Home",30.00,25,"Warm white LED lighting"),
(111,"Electric Kettle","Home",40.00,18,"1.7L fast boil kettle"),
(112,"Gaming Chair","Furniture",250.00,5,"Ergonomic high back"),
(113,"Office Chair","Furniture",120.00,7,"Mesh back support"),
(114,"Standing Desk","Furniture",300.00,4,"Height adjustable"),
(115,"Notebook Pack","Stationery",8.00,200,"Pack of 5 notebooks"),
(116,"Ballpoint Pens","Stationery",6.00,500,"Pack of 20 pens"),
(117,"Gel Pens","Stationery",10.00,150,"Smooth writing gel ink"),
(118,"Scented Candles","Home",15.00,40,"Lavender aroma"),
(119,"Water Bottle","Accessories",20.00,80,"Stainless steel insulated"),
(120,"Travel Mug","Accessories",18.00,60,"Vacuum sealed"),
(121,"Yoga Mat","Fitness",35.00,22,"Non-slip material"),
(122,"Dumbbell Set","Fitness",80.00,10,"Adjustable weight plates"),
(123,"Resistance Bands","Fitness",25.00,45,"Multi-level resistance"),
(124,"Tennis Racket","Sports",90.00,12,"Lightweight graphite"),
(125,"Soccer Ball","Sports",30.00,35,"Standard match size"),
(126,"Basketball","Sports",28.00,33,"Indoor/outdoor use"),
(127,"Running Shoes","Footwear",70.00,25,"Breathable mesh upper"),
(128,"Hiking Boots","Footwear",120.00,14,"Waterproof leather"),
(129,"Flip Flops","Footwear",15.00,60,"Comfort foam sole"),
(130,"Winter Jacket","Clothing",150.00,8,"Thermal insulated"),
(131,"T-Shirt Pack","Clothing",25.00,100,"Pack of 3 cotton shirts"),
(132,"Jeans","Clothing",45.00,40,"Slim fit denim"),
(133,"Socks Pack","Clothing",12.00,200,"Pack of 6 cotton socks"),
(134,"Backpack","Bags",50.00,20,"Laptop compatible"),
(135,"Messenger Bag","Bags",65.00,14,"Crossbody shoulder strap"),
(136,"Travel Suitcase","Bags",120.00,9,"ABS hard shell"),
(137,"Phone Charger","Electronics",15.00,100,"USB-C fast charging"),
(138,"Power Bank","Electronics",35.00,60,"10000mAh capacity"),
(139,"External Hard Drive","Electronics",80.00,25,"1TB HDD"),
(140,"HDMI Cable","Electronics",10.00,200,"2m high speed"),
(141,"Ethernet Cable","Electronics",8.00,150,"5m cat6 cable"),
(142,"Monitor 24\"","Electronics",160.00,12,"1080p IPS display"),
(143,"Monitor 27\"","Electronics",250.00,8,"1440p 75Hz display"),
(144,"Portable SSD","Electronics",120.00,20,"500GB USB 3.1"),
(145,"Budget Coffee Machine","Home",60.00,13,"12-cup brewing system"), # duplicate description test
(146,"Paper Clips Box","Stationery",3.00,3000,"Box of 200 clips"),
(147,"Promotional Keychain","Accessories",0.00,500,"Giveaway item"), # free test item
(148,"Luxury Diamond Pen","Stationery",9999.99,2,"Collector edition"),
(149,"Pricing Error Item","Misc",-10.00,10,"Should not be negative"), # negative price error
(150,"Novel Book","Books",12.00,100,"A"*300) # long text
]

c.executemany("INSERT INTO products VALUES(?,?,?,?,?,?)", products + more_products)

# Sessions
c.executemany("INSERT INTO sessions VALUES(?,?,?,?)",[
(1,1,"2025-09-01 10:00","2025-09-01 10:30"),
(1,2,"2025-09-05 09:00","2025-09-05 09:10"),
(2,1,"2025-09-05 11:00","2025-09-05 11:40"),
(3,1,"2025-09-07 12:00","2025-09-07 11:50")
])

# Viewed
c.executemany("INSERT INTO viewedProduct VALUES(?,?,?,?)",[
(1,1,"2025-09-01 10:05",101),
(1,1,"2025-09-01 10:10",102),
(2,1,"2025-09-05 11:10",103),
(3,1,"2025-09-07 12:05",999)
])

# Search
c.executemany("INSERT INTO search VALUES(?,?,?,?)",[
(1,1,"2025-09-01 10:06","laptop"),
(2,1,"2025-09-05 11:15","coffee maker"),
(3,1,"2025-09-07 12:10","brewer")
])

# Cart
c.executemany("INSERT INTO cart VALUES(?,?,?,?)",[
(1,1,101,1),
(1,2,102,2),
(2,1,103,1),
(3,1,105,2)
])

# Orders
c.executemany("INSERT INTO orders VALUES(?,?,?,?,?)",[
(9001,1,1,"2025-09-01","123 Main St Edmonton"),
(9002,2,1,"2025-09-05","456 Pine Ave Calgary"),
(9003,3,1,"2025-09-07","789 Oak Rd Vancouver")
])

c.executemany("INSERT INTO orderlines VALUES(?,?,?,?,?)",[
(9001,1,101,1,1200.00),
(9001,2,102,1,150.00),
(9002,1,103,2,80.00),
(9002,2,104,1,95.00)
])

conn.commit()
conn.close()

db_path

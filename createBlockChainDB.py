import sqlite3

con=sqlite3.connect("data/blockchain.db")
cur=con.cursor()

cur.execute("CREATE TABLE blocks(height INTEGER PRIMARY KEY, version INTEGER, hash TEXT, previousBlock TEXT, merkleRoot TEXT, timeStamp REAL, target TEXT, transactionCount INTEGER, tips INTEGER, transactions TEXT)")

con.commit()
con.close()
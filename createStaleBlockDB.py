import sqlite3 as sqlite

con=sqlite.connect("data/staleblock.db")
cur=con.cursor()

cur.execute("CREATE TABLE staleBlocks(height INTEGER PRIMARY KEY, version INTEGER, hash TEXT, previousBlock TEXT, merkleRoot TEXT, timeStamp REAL, target TEXT, transactionCount INTEGER, tips INTEGER, transactions TEXT)")
con.commit()
con.close()
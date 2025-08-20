import sqlite3

con=sqlite3.connect("data/utxoindex.db")
cur=con.cursor()

cur.execute("CREATE TABLE utxo_index(txid TEXT, hashedPubKey TEXT, vout INTEGER, lockTime INTEGER, value INTEGER)")
con.commit()
con.close()
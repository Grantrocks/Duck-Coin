import sqlite3
import json
import hashlib
con = sqlite3.connect("databases/blockchain.db")
cur = con.cursor()
cur.execute("CREATE TABLE blocks(blockHeight integer NOT NULL,blockHash text NOT NULL,header text NOT NULL,transactions text NOT NULL)")
con.commit()

"""
txcon=sqlite3.connect("databases/txqueue.db")
txcur=txcon.cursor()
txcur.execute("CREATE TABLE txs(id text NOT NULL,json text NOT NULL)")
txcon.commit()
txcur.close()
txcon.close()"""
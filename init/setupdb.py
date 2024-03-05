import sqlite3
import json
con = sqlite3.connect("blocks/blockchain.db")
cur = con.cursor()
cur.execute("CREATE TABLE blocks(blockHeight integer NOT NULL,blockHash text NOT NULL,header text NOT NULL,transactions text NOT NULL)")
con.commit()

cur.execute("INSERT INTO blocks VALUES (0,'asdfasdf','"+json.dumps({"headerstuff":112})+"','"+json.dumps([{"txid":"asdfasdfasdf"},{"txid":"asdfasdfasdfasdfasdf"},{"txid":"asdfasdfasdfasdfasdfasdfasdfasdf"}])+"')")
con.commit()
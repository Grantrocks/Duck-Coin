import sqlite3
import json

def fetchTransaction(txID,blockHeight=0):
    con = sqlite3.connect("blocks/blockchain.db")
    cur = con.cursor()
    blocks=cur.execute(f'SELECT * FROM blocks WHERE blockHeight>={blockHeight}').fetchall()
    for block in blocks:
        transactions=json.loads(block[3])
        for transaction in transactions:
            if transaction['txid']==txID:
                return transaction
    return None
    #for block in blocks:

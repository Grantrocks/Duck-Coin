import sqlite3
import json
import hashlib
def fetchTransaction(txID,blockHeight=0):
    con = sqlite3.connect("blocks/blockchain.db")
    cur = con.cursor()
    blocks=cur.execute(f'SELECT * FROM blocks WHERE blockHeight>={blockHeight}').fetchall()
    for block in blocks:
        transactions=json.loads(block[3])
        for transaction in transactions:
            if transaction['txid']==txID:
                cur.close()
                con.close()
                return transaction
    cur.close()
    con.close()
    return None
def fetchLatestBlockData():
    f=open("cache_data.json")
    data=json.load(f)
    f.close()
    blockHeight=data['blockHeight']
    con=sqlite3.connect("blocks/blockchain.db")
    cur=con.cursor()
    block=cur.execute("SELECT * FROM blocks WHERE blockHeight="+str(blockHeight)).fetchone()
    cur.close()
    con.close()
    if block:
        return block
    return False
def fetchAllBlocks():
    con=sqlite3.connect("blocks/blockchain.db")
    cur=con.cursor()
    blocks=cur.execute("SELECT * FROM blocks").fetchall()
    cur.close()
    con.close()
    return blocks
def addToTransQueue(transaction:str):
    con=sqlite3.connect("txqueue.db")
    cur=con.cursor()
    cur.execute("INSERT INTO txs VALUES ('"+hashlib.sha1(transaction.encode()).hexdigest()+"','"+transaction+"')")
    con.commit()
    cur.close()
    con.close()
    return True
def fetchTransQueue():
    con=sqlite3.connect("txqueue.db")
    cur=con.cursor()
    txs=cur.execute("SELECT * FROM txs").fetchall()
    cur.close()
    con.close()
    return txs
def fetchBlockData(blockID):
    method=None
    if type(blockID)==type("str"):
        method="blockHash"
        blockID=f"'{blockID}'"
    elif type(blockID)==type(0):
        method="blockHeight"
        blockID=f"{blockID}"
    else:
        return False
    con=sqlite3.connect("blocks/blockchain.db")
    cur=con.cursor()
    block=cur.execute("SELECT * FROM blocks WHERE "+method+"="+blockID).fetchone()
    cur.close()
    con.close()
    return block
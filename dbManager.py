import sqlite3
import json
import hashlib
def fetchTransaction(txID,blockHeight=0):
    con = sqlite3.connect("databases/blockchain.sqlite")
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
    con=sqlite3.connect("databases/blockchain.sqlite")
    cur=con.cursor()
    block=cur.execute("SELECT * FROM blocks WHERE blockHeight="+str(blockHeight)).fetchone()
    cur.close()
    con.close()
    if block:
        return block
    return False
def fetchAllBlocks():
    con=sqlite3.connect("databases/blockchain.sqlite")
    cur=con.cursor()
    blocks=cur.execute("SELECT * FROM blocks").fetchall()
    cur.close()
    con.close()
    return blocks
def addToTransQueue(transaction:str):
    con=sqlite3.connect("databases/txqueue.sqlite")
    cur=con.cursor()
    cur.execute("INSERT INTO txs VALUES ('"+hashlib.sha1(transaction.encode()).hexdigest()+"','"+transaction+"')")
    con.commit()
    cur.close()
    con.close()
    return True
def fetchTransQueue():
    con=sqlite3.connect("databases/txqueue.sqlite")
    cur=con.cursor()
    txs=cur.execute("SELECT * FROM txs").fetchall()
    cur.close()
    con.close()
    return txs
def fetchBlockData(blockID):
    method=None
    if type(blockID)==type(""):
        method="blockHash"
        blockID=f"'{blockID}'"
    elif type(blockID)==type(0):
        method="blockHeight"
        blockID=f"{blockID}"
    else:
        return False
    con=sqlite3.connect("databases/blockchain.sqlite")
    cur=con.cursor()
    block=cur.execute("SELECT * FROM blocks WHERE "+method+"="+blockID).fetchone()
    cur.close()
    con.close()
    return block
def fetchTransactionsByPubKey(pubKey,addr):
  blocks=fetchAllBlocks()
  transactions=[]
  for block in blocks:
    for tx in json.loads(block[3]):
      added=False
      for inp in tx['inputs']:
        if inp['scriptSig']['pubKey']==pubKey:
          transactions.append(tx)
          added=True
          continue
      if not added:
        for out in tx['outputs']:
            if out['scriptPubKey']==addr:
                transactions.append(tx)
                continue
  return transactions
def removeFromTransQueue(dbIDS):
    con=sqlite3.connect("databases/txqueue.sqlite")
    cur=con.cursor()
    for dbID in dbIDS:
        cur.execute("DELETE FROM txs WHERE id='"+dbID+"'")
    con.commit()
    cur.close()
    con.close()
    return True
def appendBlock(block):
    blockHeight=block['header']['height']
    blockHash=block['header']['hash']
    header=json.dumps(block['header'])
    transactions=json.dumps(block['transactions'])
    con=sqlite3.connect("databases/blockchain.sqlite")
    cur=con.cursor()
    cur.execute("INSERT INTO blocks VALUES ("+str(blockHeight)+",'"+blockHash+"','"+header+"','"+transactions+"')")
    con.commit()
    cur.close()
    con.close()
    return True
def fetchDbIDS():
    con=sqlite3.connect("databases/txqueue.sqlite")
    cur=con.cursor()
    dbIDS=cur.execute("SELECT id FROM txs").fetchall()
    cur.close()
    con.close()
    return dbIDS
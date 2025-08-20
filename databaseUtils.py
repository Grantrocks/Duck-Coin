import sqlite3 as sqlite
import json
def fetchBlockHeight(): # This function returns the current block height.
    con=sqlite.connect("data/blockchain.db")
    cur=con.cursor()
    cur.execute("SELECT COUNT(*) FROM blocks")
    leng=cur.fetchone()[0]-1
    con.close()
    return leng
def fetchBlock(blockHeight:int):
    con=sqlite.connect("data/blockchain.db")
    cur=con.cursor()
    cur.execute("SELECT * FROM blocks WHERE height="+str(blockHeight))
    return cur.fetchone()
def getUTXO(utxo:str,vout:int): # This function scans for a UTXO already in the UTXO index.
    con=sqlite.connect("data/utxoindex.db")
    cur=con.cursor()
    cur.execute("SELECT * FROM utxo_index WHERE txid='"+str(utxo)+"' AND vout="+str(vout))
    result=cur.fetchall()
    con.close()
    return result
def removeUTXO(utxo:str,vout:int):
    if len(getUTXO(utxo,vout))==0:
        print("UTXO DOESENT EXIST")
        return False
    try:
        con=sqlite.connect("data/utxoindex.db")
        cur=con.cursor()
        cur.execute("DELETE FROM utxo_index WHERE txid='"+str(utxo)+"' AND vout="+str(vout))
        con.commit()
        con.close()
        return True
    except Exception as e:
        return e
    
def addBlock(block:dict,blockHeight):
    try:
        con=sqlite.connect("data/blockchain.db")
        cur=con.cursor()
        transactions=json.dumps(block.toJSON()['transactions'])
        cur.execute(f"INSERT INTO blocks VALUES ({blockHeight},{block.version},'{block.hash}','{block.previousBlock}','{block.merkleRoot}',{block.timeStamp},'{block.target}',{block.transactionCount},{block.tips},'{transactions}')")
        con.commit()
        return True
    except Exception as e:
        return e
def addUTXOS(transactions:list,height:int):
    try:
        con=sqlite.connect("data/utxoindex.db")
        cur=con.cursor()
        for tx in transactions:
            if tx.inputs[0].scriptSig!="coinbase" and tx.inputs[0].txid!="0000000000000000000000000000000000000000000000000000000000000000":
                for o in range(0,len(tx.outputs)):
                    output=tx.outputs[o]
                    cur.execute(f"INSERT INTO utxo_index VALUES ('{tx.txid}','{output.scriptPubKeyHash}',{o},{height+2},{output.value})")
            else:
                cur.execute(f"INSERT INTO utxo_index VALUES ('{tx.txid}','{tx.outputs[0].scriptPubKeyHash}',0,{height+5},{tx.outputs[0].value})")
        con.commit()
        con.close()
        return True
    except Exception as e:
        return e
def addStaleBlock(block:dict,blockHeight:int):
    try:
        con="data/staleblock.db"
        cur=con.cursor()
        transactions=json.dumps(block.toJSON()['transactions'])
        cur.execute(f"INSERT INTO staleBlocks VALUES ({blockHeight},{block.version},'{block.hash}','{block.previousBlock}','{block.merkleRoot}',{block.timeStamp},'{block.target}',{block.transactionCount},{block.tips},'{transactions}')")
        con.commit()
    except Exception as e:
        return e
def addOrphanBlock(block:dict,blockHeight:int):
    try:
        con="data/orphan.db"
        cur=con.cursor()
        transactions=json.dumps(block.toJSON()['transactions'])
        cur.execute(f"INSERT INTO orphans VALUES ({blockHeight},{block.version},'{block.hash}','{block.previousBlock}','{block.merkleRoot}',{block.timeStamp},'{block.target}',{block.transactionCount},{block.tips},'{transactions}')")
        con.commit()
    except Exception as e:
        return e
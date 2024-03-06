import hashlib
import json
import base58
import dbManager
import binascii
import ecdsa
import datetime

# Initialization
print("Initializing node....")

blocks=dbManager.fetchAllBlocks()

f=open("cache_data.json")
data=json.load(f)
f.close()
data['blockHeight']=blocks[-1][0]
f=open("cache_data.json","w")
json.dump(data,f,indent=6)
f.close()
print("Done")
# Classes

class MemoryPool:
    transactions=[]

class Block:
    header={
        "hash":"",
        "height":0,
        "last_block_hash":"",
        "merkle_root":"",
        "time":0,
        "target":"",
        "nonce":0
    }
    transactions=[]

class Transaction:
    inputCount=0
    inputs=[]
    outputCount=0
    outputs=[]
    created=0

class Input:
    txid=""
    out=""
    scriptSig={"pubKey":"","signature":""}
class OutPut:
    value=0
    scriptPubKey=""



# Functions
def generateAddressFromPubkey(pubKey:str):
    hashofPub = hashlib.sha3_256(binascii.unhexlify(pubKey)).hexdigest()
    ripeMDofhashOfPub = hashlib.new('ripemd160', binascii.unhexlify(hashofPub))
    prependNetworkByte = '17' + ripeMDofhashOfPub.hexdigest()
    hash = prependNetworkByte
    for x in range(1,3):
        hash = hashlib.sha3_256(binascii.unhexlify(hash)).hexdigest()
    cheksum = hash[:8]
    appendChecksum = prependNetworkByte + cheksum
    return base58.b58encode(binascii.unhexlify(appendChecksum))


def verifyTXOwnership(pubKey:str,signature:str,outputSelect:int,txID:str,txJSON:json):
    transaction=txJSON
    if outputSelect>transaction['outputCount']:
        return False
    output=transaction['outputs'][outputSelect]
    OldPub=output['scriptPubKey']
    newOldPub=generateAddressFromPubkey(pubKey)
    if newOldPub!=OldPub:
        return False
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubKey[2:]), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha3_256)
    return vk.verify(bytes.fromhex(signature), txID.encode())

def createTransaction(pubKey:str,recipient:str,outputSelect:int,SigTX:list,amount:int):
    txDataList=[]
    for txID in SigTX:
        txID=txID[1]
        signature=txID[0]
        tx=dbManager.fetchTransaction(txID)
        txDataList.append(txDataList)
        if not verifyTXOwnership(pubKey,signature,outputSelect,txID,tx):
            return 1
    inputs=[]
    totalAvalAmount=0
    for tx in txDataList:
        temptxID=tx['txid']
        for output in tx['outputs']:
            totalAvalAmount+=output['value']
        inp=Input
        inp.out=outputSelect
        inp.txid=temptxID
        inp.scriptSig['pubKey']=pubKey
        inp.scriptSig['signature']=signature
        txJSON=json.dumps(inp)
        inputs.append(txJSON)
    outputs=[]
    out=OutPut
    out.value=amount
    out.scriptPubKey=recipient
    outputs.append(json.dumps(out))
    remaining=totalAvalAmount-amount
    if remaining<0:
        return 2
    if remaining>0:
        remainingOut=OutPut
        remainingOut.value=remaining
        remainingOut.scriptPubKey=generateAddressFromPubkey(pubKey)
        outputs.append(json.dumps(remainingOut))
    transaction=Transaction
    transaction.inputCount=len(inputs)
    transaction.inputs=inputs
    transaction.outputCount=len(outputs)
    transaction.outputs=outputs
    transaction.created=datetime.datetime.now()
    return dbManager.addToTransQueue(json.dumps(transaction))


def coinbaseTransaction(recipient:str):
    input={"txid":"COINBASE"}
    out=OutPut
    out.amount=500000000
    out.scriptPubKey=recipient
    transaction=Transaction
    transaction.inputCount=1
    transaction.outputCount=1
    transaction.inputs=input
    transaction.outputs=out
    transaction.created=datetime.datetime.now()
    return json.dumps(transaction)

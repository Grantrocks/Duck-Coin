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

class Block:
    def __init__(self,header:json,transactions:list,dbIDS:list):
        self.header=header
        self.transactions=transactions
        self.dbIDS=dbIDS

class Transaction:
    def __init__(self,inputCount:int,inputs:list,outputCount:int,outputs:list,created:int):
        self.inputCount=inputCount
        self.inputs=inputs
        self.outputCount=outputCount
        self.outputs=outputs
        self.created=created

class Input:
    def __init__(self,txid:str,out:str,scriptSig:json):
        self.txid=""
        self.out=""
        self.scriptSig=scriptSig
class OutPut:
    def __init__(self,value:int,scriptPubKey:str):
        self.value=value
        self.scriptPubKey=scriptPubKey


  

# Functions
def merkle_root_hash(data):
    if len(data) == 1:
        return data[0]

    new_data = []
    for i in range(0, len(data), 2):
        left = data[i]
        right = data[i+1] if i+1 < len(data) else left
        combined = left + right
        new_data.append(hashlib.sha3_256(combined.encode()).hexdigest())

    return merkle_root_hash(new_data)

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

def calculate_new_target_hash(old_target_hash, quotient):
    old_target = int(old_target_hash, 16)
    if quotient>=3:
        quotient=3
    new_target = int(old_target * quotient)
    new_target_bytes = hex(new_target)[2:]
    remaining=64-len(new_target_bytes)
    addition="0"*remaining
    return addition+new_target_bytes

def verifyUnspentsGetBalance(txids:list,senderaddr:str,senderPubKey:str):
    blocks=dbManager.fetchAllBlocks()
    spent=[]
    balance=0
    for block in blocks:
        for tx in block[3]:
            tx=json.loads(tx)
            sending=False
            for inp in tx['inputs']:
                if inp['scriptSig']["pubKey"]==senderPubKey:
                    sending=True
                if inp['txid'] in txids:
                    spent.append(inp['txid'])
            for out in tx['outputs']:
                if not sending:
                    if out['scriptPubKey']==senderaddr:
                        balance+=out['value']
                if sending:
                    if out['scriptPubKey']!=senderaddr:
                        balance-=out['value']
    return [spent,balance]

def verifyTXOwnership(pubKey:str,signature:str,outputSelect:int,txID:str,txJSON:json):
    transaction=txJSON
    if outputSelect>transaction['outputCount']:
        return False
    f=open("cache_data.json")
    cachedata=json.load(f)
    if transaction['locktime']<cachedata['blockHeight']+10:
        return False
    output=transaction['outputs'][outputSelect]
    OldPub=output['scriptPubKey']
    newOldPub=generateAddressFromPubkey(pubKey)
    if newOldPub!=OldPub:
        return False
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubKey[2:]), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha3_256)
    return vk.verify(bytes.fromhex(signature), txID.encode())

def createTransaction(pubKey:str,recipient:str,SigTX:list,amount:int):
    txDataList=[]
    txidList=[]
    for txID in SigTX:
        signature=txID[0]
        output=txID[2]
        txID=txID[1]
        txidList.append(txID)
        signature=txID[0]
        tx=dbManager.fetchTransaction(txID)
        txDataList.append([tx,output])
        if not verifyTXOwnership(pubKey,signature,output,txID,tx):
            return 1
    verifyIfOwnerCanSend=verifyUnspentsGetBalance(txids=txidList,senderaddr=generateAddressFromPubkey(pubKey),pubKey=pubKey)
    print(verifyIfOwnerCanSend)
    inputs=[]
    totalAvalAmount=0
    for tx in txDataList:
        temptxID=tx[0]['txid']
        for output in tx[0]['outputs']:
            totalAvalAmount+=output['value']
        inp=Input(out=tx[1],txid=temptxID,scriptSig={"pubKey":pubKey,"signature":signature})
        txJSON=vars(inp)
        inputs.append(txJSON)
    outputs=[]
    out=OutPut(value=amount,scriptPubKey=recipient)
    outputs.append(vars(out))
    remaining=totalAvalAmount-amount
    if remaining<0:
        return 2
    if remaining>0:
        remainingOut=OutPut(value=remaining,scriptPubKey=generateAddressFromPubkey(pubKey))
        outputs.append(vars(remainingOut))
    transaction=Transaction(inputCount=len(inputs),inputs=inputs,outputCount=len(outputs),outputs=outputs,created=datetime.datetime.now().timestamp())    
    return dbManager.addToTransQueue(json.dumps(vars(transaction)))
    
def coinbaseTransaction(recipient:str):
    input={"txid":"","scriptSig":{"pubKey":"COINBASE","signature":"waddle"}}
    out=OutPut(500000000,recipient)
    transaction=Transaction(inputCount=1,outputCount=1,inputs=[input],outputs=[vars(out)],created=datetime.datetime.now().timestamp())
    return vars(transaction)

def createBlock(blockCreator):
    configF=open("permConfig.json")
    config=json.load(configF)
    configF.close()
    cacheF=open("cache_data.json")
    cache=json.load(cacheF)
    cacheF.close()
    transactions=[]
    transactionsHASHES=[]
    coinbaseTX=coinbaseTransaction(blockCreator)
    coinbaseTX['locktime']=cache["blockHeight"]+2
    coinbaseTX['txid']=hashlib.sha3_256(hashlib.sha3_256(json.dumps(coinbaseTX).encode()).hexdigest().encode()).hexdigest()
    transactions.append(coinbaseTX)
    dbIDS=[]
    for tx in dbManager.fetchTransQueue():
        txJSON=json.loads(tx[1])
        txJSON['locktime']=config['blockHeight']+2
        txJSON['txid']=hashlib.sha3_256(hashlib.sha3_256(json.dumps(txJSON).encode())).hexdigest()
        transactions.append(txJSON)
        dbIDS.append(tx[0])
    for tx in transactions:
        transactionsHASHES.append(tx['txid'])
    merkle_root=merkle_root_hash(transactionsHASHES)
    target=config['startDiff']
    if cache['blockHeight']!=0:
        cur_block=json.loads(dbManager.fetchBlockData(cache['blockHeight'])[2])['header']
        cur_block=cur_block['time']
        old_block=json.loads(dbManager.fetchBlockData(cache['blockHeight']-1)[2])['header']
        quotient=(cur_block-old_block['time'])/300
        target=calculate_new_target_hash(cur_block['target'],quotient)
        lastHash=old_block['hash']
    else:
        lastHash="2024 March 7 And Duino Coin is at risk of shutting down. Due to this I created this currency to try and replace it."
    header={
            "version":config['version'],
            "height":cache["blockHeight"],
            "last_block_hash":lastHash,
            "merkle_root":merkle_root,
            "time":datetime.datetime.now().timestamp(),
            "target":target
        }
    block=Block(header,transactions,dbIDS)
    return vars(block)
def getCandidateBlock(creator=""):
    f=open("candidate.json")
    candidate=json.load(f)
    f.close()
    if candidate['header']['txid']=="2024 March 7 And Duino Coin is at risk of shutting down. Due to this I created this currency to try and replace it.":
        candidate=createBlock(creator)
        f=open("candidate.json","w")
        json.dump(candidate,f)
        f.close()
        return candidate
    else:
        return candidate
def validateBlock(nonce,hash,blockheight):
    print()
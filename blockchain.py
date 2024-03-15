import hashlib
import json
import base58
import dbManager
import binascii
import ecdsa
import datetime

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
        self.txid=txid
        self.out=out
        self.scriptSig=scriptSig
class OutPut:
    def __init__(self,value:int,scriptPubKey:str):
        self.value=value
        self.scriptPubKey=scriptPubKey

# Functions
def getBalance(pubKey):
  blocks=dbManager.fetchAllBlocks()
  balance=0
  for block in blocks:
      TXLST=json.loads(block[3])
      for tx in TXLST:
          sending=False
          for inp in tx['inputs']:
              if inp['scriptSig']["pubKey"]==pubKey:
                  sending=True
          for out in tx['outputs']:
              if not sending:
                  if out['scriptPubKey']==generateAddressFromPubkey(pubKey):
                      balance+=out['value']
              elif sending:
                  if out['scriptPubKey']!=generateAddressFromPubkey(pubKey):
                      balance-=out['value']
  return balance
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
    return base58.b58encode(binascii.unhexlify(appendChecksum)).decode()

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
    for block in blocks:
        TXLST=json.loads(block[3])
        for tx in TXLST:
            for inp in tx['inputs']:
                if inp['txid'] in txids:
                    spent.append(inp['txid'])
    return [spent]

def verifyTXOwnership(pubKey:str,signature:str,outputSelect:int,txID:str,txJSON):
    transaction=txJSON
    if outputSelect>transaction['outputCount']:
        print("[SERVER] Selected output is larget than tx output count")
        return False
    blockHeight=len(dbManager.fetchAllBlocks())-1
    if transaction['locktime']>blockHeight:
        print("[SERVER] Transaction is locked")
        return False
    output=transaction['outputs'][outputSelect]
    OldPub=output['scriptPubKey']
    newOldPub=generateAddressFromPubkey(pubKey)
    if newOldPub!=OldPub:
        print("[SERVER] Transaction is not owned by sender")
        return False
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubKey[2:]), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha3_256)
    return vk.verify(bytes.fromhex(signature), txID.encode())
def checkIfTxNotInMemPool(txidlist):
  txs=dbManager.fetchTransQueue()
  for tx in txs:
    txdatals=json.loads(tx[1])
    for txdata in txdatals['inputs']:
      for txid in txidlist:
        if txid[0]==txdata['txid']:
          return False
        if txid[1]==txdata['out']:
          return False
  return False
def createTransaction(pubKey:str,recipient:str,SigTX:list,amount:int):
    if recipient==generateAddressFromPubkey(pubKey):
        print("[SERVER] You cannot send to yourself")
        return 6
    txDataList=[]
    txidList=[]
    txOUTHASHLIST=[]
    for txID in SigTX:
        signature=txID[0]
        output=txID[2]
        txIDS=txID[1]
        txOUTHASHLIST.append([txIDS,output])
        txidList.append(txID)
        tx=dbManager.fetchTransaction(txIDS)
        txDataList.append([tx,output])
        if not verifyTXOwnership(pubKey,signature,output,txIDS,tx):
            return 1
    verifyIfOwnerCanSend=verifyUnspentsGetBalance(txids=txidList,senderaddr=generateAddressFromPubkey(pubKey),senderPubKey=pubKey)
    if len(verifyIfOwnerCanSend[0])!=0:
      return 4
    inMemPool=checkIfTxNotInMemPool(txOUTHASHLIST)
    if inMemPool:
      return 5
    inputs=[]
    totalAvalAmount=0
    for tx in txDataList:
        temptxID=tx[0]['txid']
        for output in tx[0]['outputs']:
            if output['scriptPubKey']==generateAddressFromPubkey(pubKey):
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
    blockHeight=len(dbManager.fetchAllBlocks())
    transactions=[]
    transactionsHASHES=[]
    coinbaseTX=coinbaseTransaction(blockCreator)
    coinbaseTX['locktime']=blockHeight+config['lockTime']
    coinbaseTX['txid']=hashlib.sha3_256(hashlib.sha3_256(json.dumps(coinbaseTX).encode()).hexdigest().encode()).hexdigest()
    transactions.append(coinbaseTX)
    dbIDS=[]
    for tx in dbManager.fetchTransQueue():
        txJSON=json.loads(tx[1])
        txJSON['locktime']=(blockHeight-1)+2
        txJSON['txid']=hashlib.sha3_256(hashlib.sha3_256(json.dumps(txJSON).encode()).hexdigest().encode()).hexdigest()
        transactions.append(txJSON)
        dbIDS.append(tx[0])
    for tx in transactions:
        transactionsHASHES.append(tx['txid'])
    merkle_root=merkle_root_hash(transactionsHASHES)
    if blockHeight!=0:
        lBlock=json.loads(dbManager.fetchBlockData(blockHeight-1)[2])
        target=lBlock['target']
        if blockHeight%8==0:
          old_block=json.loads(dbManager.fetchBlockData(blockHeight-8)[2])
          cur_block=lBlock
          quotient=(cur_block['time']-old_block['time'])/2400
          target=calculate_new_target_hash(cur_block['target'],quotient)
        lastHash=lBlock['hash']
    else:
        target=config['startDiff']
        lastHash="2024 March 7 And Duino Coin is at risk of shutting down. Due to this I created this currency to try and replace it."
    header={
            "version":config['version'],
            "height":blockHeight,
            "last_block_hash":lastHash,
            "merkle_root":merkle_root,
            "time":datetime.datetime.now().timestamp(),
            "target":target
        }
    block=Block(header,json.dumps(transactions),dbIDS)
    return vars(block)
def validateBlock(candidate):
    c=candidate['header']
    checkHash=hashlib.sha3_256(hashlib.sha3_256(f"{str(c['version'])}{str(c['height'])}{c['last_block_hash']}{c['merkle_root']}{str(c['time'])}{c['target']}{str(c['nonce'])}".encode()).hexdigest().encode()).hexdigest()
    if candidate['header']['hash']!=checkHash:
        print("[SERVER] Failed Hash Check")
        return False
    targ=int(candidate['header']['target'],16)
    incheck=int(checkHash,16)
    if not incheck<=targ:
        print("[SERVER] Failed Target Check")
        return False
    bhs=dbManager.fetchAllBlocks()
    if len(bhs)>0:
      for height in bhs[0]:
        if height==candidate['header']['height']:
          print("[SERVER] Block already exists")
          return False
    if candidate['header']['height']!=0:
        prev=json.loads(dbManager.fetchBlockData(candidate['header']['height']-1)[2])
        if not candidate['header']['time']>prev['time']:
            print("[SERVER] This block cannot be older that the last block")
            return False
    validDBIDS=dbManager.fetchDbIDS()
    validDBIDSF=[]
    for dbv in validDBIDS:
      validDBIDSF.append(dbv[0])
    txIDLIST=[]
    candidate['transactions']=json.loads(candidate['transactions'])
    for tx in range(len(candidate['transactions'])):
      jsondata=candidate['transactions']
      txd=jsondata[tx]
      txIDLIST.append(txd['txid'])
      if txd['inputs'][0]['scriptSig']['pubKey']=="COINBASE":
        continue
      dbID=candidate['dbIDS'][tx-1]
      temptx=json.loads(json.dumps(txd))
      del temptx['txid']
      del temptx['locktime']
      sha1Hash=hashlib.sha1(json.dumps(temptx).encode())
      if dbID!=sha1Hash.hexdigest():
        print("[SERVER] INVALID TRANSACTION ID")
        return False
      if not sha1Hash.hexdigest() in validDBIDSF:
        print("[SERVER] Transaction inside block not known")
        return False
    merk=merkle_root_hash(txIDLIST)
    if merk!=candidate['header']['merkle_root']:
        print("[SERVER] Invalid merkle root")
        return False
    return True
def addBlock(block,nextBlockCreator):
    if not validateBlock(block):
        return False
    added=dbManager.appendBlock(block)
    if not added:
        return False
    rm=dbManager.removeFromTransQueue(block['dbIDS'])
    if not rm:
      return False
    return True
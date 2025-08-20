import socket
import blockchain
import databaseUtils
from datetime import datetime
from hashlib import sha3_256
import ecdsa
import os
import json
mempool=[]
version=0 # DO NOT TOUCH THIS VALUE

def base58_encode(data: bytes):
    """Encode bytes to a Base58 string."""
    # Convert big-endian bytes to integer
    num = int.from_bytes(data, byteorder='big')
    encode = ''
    while num > 0:
        num, rem = divmod(num, 58)
        encode = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'[rem] + encode
    # Add '1' for each leading 0 byte
    for byte in data:
        if byte == 0:
            encode = '1' + encode
        else:
            break
    return encode


def base58_check_encode(payload: bytes):
    """Encode payload with Base58Check: payload + checksum (4 bytes of double-SHA256)."""
    checksum = sha3_256(sha3_256(payload).digest()).digest()[:4]
    return base58_encode(payload + checksum)


def generate_keypair():
    """
    Generate ECDSA SECP256k1 key pair.
    Returns (private_key_bytes, public_key_bytes_uncompressed).
    """
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    private_key = sk.to_string()
    public_key = b'\x04' + vk.to_string()  # uncompressed format prefix 0x04
    return private_key.hex(), public_key.hex()

def generate_address(public_key: bytes):
    """
    Generate address:
    - Hash public key with SHA3-256.
    - Truncate hash to 20 bytes (like RIPEMD160).
    - Prepend version byte (0x1E for addresses starting with 'D').
    - Base58Check encode.
    """
    sha3_hash = sha3_256(public_key).digest()
    pubkey_hash_20 = sha3_hash[:20]
    version_byte = b'\x1E'  # Decimal 30, prefix 'D'
    payload = version_byte + pubkey_hash_20
    address = base58_check_encode(payload)
    return address

def verifyINTXSignature(publicKey:str,signature:str,t:dict):
    vk=ecdsa.VerifyingKey.from_string(bytes.fromhex(publicKey),curve=ecdsa.SECP256k1,hashfunc=sha3_256)
    txdata=str(t.version)+str(t.inputCount)+str(t.outputCount)+str(t.timeStamp)
    for tx in t.inputs:
        txdata+=str(tx.txid)+str(tx.vout)
    for tx in t.outputs:
        txdata+=str(tx.value)+str(tx.scriptPubKeyHash)
    data=sha3_256(sha3_256(txdata.encode()).digest()).digest()
    try:
        return vk.verify_digest(bytes.fromhex(signature),data)
    except ecdsa.BadSignatureError:
        return False
def calculateLeftoverDuckoshi(transaction:dict):
    totalIn=0
    totalOut=0
    for inp in transaction.inputs:
        if inp.txid=="0000000000000000000000000000000000000000000000000000000000000000" and inp.vout==0 and inp.scriptSig=="coinbase":
            return 0
        utxo=databaseUtils.getUTXO(inp.txid,inp.vout)
        if len(utxo)==0:
            return 0
        utxo=utxo[0]
        totalIn+=utxo[4]
    for out in transaction.outputs:
        totalOut+=out.value
    return totalIn-totalOut
def checkUTXOUnlock(input:dict,transaction:dict):
    try:
        currentBlockHeight=databaseUtils.fetchBlockHeight()
        utxo=databaseUtils.getUTXO(input.txid,input.vout)
        if len(utxo)!=1:
            print("INVALID UTXO DOES NOT EXIST")
            return False
        utxo=utxo[0]
        lockTime=utxo[3]
        utxoHashedPubKey=utxo[1]
        inputScriptSig=input.scriptSig.split(";")
        pubKey=inputScriptSig[0]
        if utxoHashedPubKey!=generate_address(bytes.fromhex(pubKey)):
            print("PUBKEY DOES NOT MATCH HASHEDPUB")
            return False
        signature=inputScriptSig[1]
        validSig=verifyINTXSignature(pubKey,signature,transaction)
        if not validSig:
            print("BAD SIGNATURE")
            return False
        if not lockTime<=currentBlockHeight:
            print("UTXO NOT UNLOCKED")
            return False
        for tx in mempool:
            for txinput in tx.inputs:
                if txinput.txid==utxo[0] and txinput.vout==utxo[2]:
                    print("DOUBLE SPEND FAIL")
                    return False
        return utxo[4]
    except Exception as e:
        print(e)
        return False
def blockReward(blockHeight:int):
    halveInterval=blockHeight%600000
    reward=3000000000
    if halveInterval==0:
        halveCount=blockHeight//600000
        reward=reward//(2**halveCount)
    return reward

def merkle_root_hash(data):
    if len(data) == 1:
        return data[0]
    new_data = []
    for i in range(0, len(data), 2):
        left = data[i]
        right = data[i+1] if i+1 < len(data) else left
        combined = left + right
        new_data.append(sha3_256(combined.encode()).hexdigest())
    return merkle_root_hash(new_data)

def getBlock(blockHeight:int):
    res=databaseUtils.fetchBlock(blockHeight)
    transasctions=[]
    for tx in json.loads(res[9]):
        inputs=[]
        outputs=[]
        for inp in tx['inputs']:
            txin=blockchain.input(inp['txid'],inp['vout'],inp['scriptSig'])
            inputs.append(txin)
        for outp in tx['outputs']:
            txout=blockchain.output(outp['value'],outp['scriptPubKeyHash'])
            outputs.append(txout)
        t=blockchain.transaction(tx['version'],inputs,outputs,tx['inputCount'],tx['outputCount'],tx['timeStamp'],tx['txid'])
        transasctions.append(t)
    block=blockchain.block(version=res[1],hash=res[2],previousBlock=res[3],merkleRoot=res[4],timeStamp=res[5],target=res[6],transactionCount=res[7],tips=res[8],transactions=transasctions)
    return block

def calculate_new_target_hash(old_target_hash, quotient):
    old_target = int(old_target_hash, 16)
    if quotient>=3:
        quotient=3
    new_target = int(old_target * quotient)
    new_target_bytes = hex(new_target)[2:]
    remaining=64-len(new_target_bytes)
    addition="0"*remaining
    return addition+new_target_bytes

def newTransaction(t:dict):
    try:
        """
        Error Codes:
            - 0 "TRANSACTION OK, ADDED TO MEMPOOL"
            - 1 "UTXO UNLOCK FAILED FOR ONE OF THE INPUTS, PLEASE CHECK THAT ALL UTXO'S ARE SPENDABLE"
            - 2 "YOU MUST PAY A 2 DUCKOSHI FEE FOR EACH TRANSACTION"
            - 4 "YOU CANNOT SEND NEGATIVE COINS IN A OUTPUT"
            - 5 "OUTPUT VALUES MUST BE INTEGERS"
            - 6 "AN ERROR OCCURED, PLEASE CHECK ALL DATA IS INPUTTED CORRECTLY"
            - 7 "TRANSACTION HAS NOT REACHED LOCKTIME"
        """
        curHeight=databaseUtils.fetchBlockHeight()
        #t=blockchain.transaction(version=0,inputs=inputs,outputs=outputs,outputCount=len(outputs),inputCount=len(inputs),timeStamp=datetime.now().timestamp(),tip=tip)
        totalValueIn=0
        totalValueOut=0
        for tx in t.inputs:
            checkutxoresult=checkUTXOUnlock(tx,t)
            if not checkutxoresult:
                return 1
            if not checkutxoresult>=curHeight:
                return 7
            totalValueIn+=checkutxoresult
        for tx in t.outputs:
            if tx.value<0:
                return 4
            if type(tx.value)!=int:
                return 5
            totalValueOut+=tx.value
        leftOver=(totalValueIn-totalValueOut)-2
        if leftOver<0:
            return 2
        txdata=str(t.version)+str(t.inputCount)+str(t.outputCount)+str(t.timeStamp)
        for tx in t.inputs:
            txdata+=str(tx.txid)+str(tx.vout)+str(tx.scriptSig)
        for tx in t.outputs:
            txdata+=str(tx.value)+str(tx.scriptPubKeyHash)
        txid=sha3_256(sha3_256(txdata.encode()).digest()).hexdigest()
        if txid!=t.txid:
            return False
        mempool.append(t)
        return 0
    except Exception as e:
        print(e)
        return 6
def getTargetQuotent(blockHeight):
    b2=getBlock(blockHeight)
    b1=getBlock(blockHeight-49)
    diff=(b2.timeStamp-b1.timeStamp)/15000 #5 minutes=300secs*50
    return diff
    
def generateCanaditBlock(hashedPubKey:str):
    blockHeight=databaseUtils.fetchBlockHeight()
    prevBlock=None
    if not blockHeight==-1:
        prevBlock=getBlock(blockHeight)
    if not prevBlock:
        target="000000f000000000000000000000000000000000000000000000000000000000"
        prevBlockHash="The date is 8/1/2025, im on vacation in hawaii and just a few days ago there was a tsunami that hit us. We were hiking in the mountains and on the way back we got a bunch of warnings about the tsunami on our phones. It sent the entire island into complete chaos and scared everyone. Nothing really happened though. Crazyshit."
    else:
        target=prevBlock.target
        if (blockHeight+1)%50==0:
            target=calculate_new_target_hash(target,getTargetQuotent(blockHeight))
        prevBlockHash=prevBlock.hash
    transactions=[]
    txidList=[]
    totalTip=0
    for tx in mempool:
        transactions.append(tx)
    for tx in transactions[1:]:
        mempool.remove(tx)   
    for tx in transactions: 
        totalTip+=calculateLeftoverDuckoshi(tx)
        txidList.append(tx.txid)
    t=blockchain.coinbaseTransaction(version=0,reward=blockReward(blockHeight),hashedPubKey=hashedPubKey,timeStamp=datetime.now().timestamp())
    transactions.append(t)
    transactions.reverse()
    transactions[0].outputs[0].value+=totalTip
    txdata=str(t.version)+str(t.inputCount)+str(t.outputCount)+str(t.timeStamp)
    for tx in t.inputs:
        txdata+=str(tx.txid)+str(tx.vout)+str(tx.scriptSig)
    for tx in t.outputs:
        txdata+=str(tx.value)+str(tx.scriptPubKeyHash)
    t.txid=sha3_256(sha3_256(txdata.encode()).digest()).hexdigest()
    txidList.append(t.txid)
    txidList.reverse()
    merkle_root=merkle_root_hash(txidList)
    block=blockchain.block(0,prevBlockHash,merkle_root,datetime.now().timestamp(),target,len(transactions),transactions,totalTip)
    return block
def jsonToTransactionDict(tx):
    inps=[]
    outputs=[]
    for inp in tx['inputs']:
        inps.append(blockchain.input(inp['txid'],inp['vout'],inp['scriptSig']))
    for out in tx['outputs']:
        outputs.append(blockchain.output(out['value'],out['scriptPubKeyHash']))
    return blockchain.transaction(tx['version'],inps,outputs,tx['inputCount'],tx['outputCount'],tx['timeStamp'],tx['txid'])
def jsonToBlockDict(jsonData):
    transactions=[]
    for tx in jsonData['transactions']:
        inps=[]
        outputs=[]
        for inp in tx['inputs']:
            inps.append(blockchain.input(inp['txid'],inp['vout'],inp['scriptSig']))
        for out in tx['outputs']:
            outputs.append(blockchain.output(out['value'],out['scriptPubKeyHash']))
        transactions.append(blockchain.transaction(tx['version'],inps,outputs,tx['inputCount'],tx['outputCount'],tx['timeStamp'],tx['txid']))
    return blockchain.block(jsonData['version'],jsonData['previousBlock'],jsonData['merkleRoot'],jsonData['timeStamp'],jsonData['target'],jsonData['transactionCount'],transactions,jsonData['tips'],jsonData['hash'],jsonData['nonce'])
def addBlock(block:dict):

    # SYSTEM NEEDED TO HANDLE 2 BLOCKS RECIVED FOR THE SAME HEIGHT. LIKE BITCOINS STALE BLOCK SYSTEM WHERE THE CHAIN WITH THE NEXT HIGHEST ONE WINS THE STANDOFF.
    




    blockHeight=databaseUtils.fetchBlockHeight()
    prevblock=getBlock(blockHeight)

    if not block.timeStamp>=prevblock.timeStamp:
        print("Failed timestamp")
        return False
    
    txids=[]
    totalTips=0
    passcount=1
    for tx in block.transactions:
        passcount+=1
        totalTips+=calculateLeftoverDuckoshi(tx)
        for input in tx.inputs:
            if input.txid=="0000000000000000000000000000000000000000000000000000000000000000" and input.vout==0 and input.scriptSig=="coinbase":
                pass
            else:
                utxocheck=checkUTXOUnlock(input,tx)
                if not utxocheck>=blockHeight:
                    print("UTXO CHECK FAIL")
                    return False
        txdata=str(tx.version)+str(tx.inputCount)+str(tx.outputCount)+str(tx.timeStamp)
        for txin in tx.inputs:
            txdata+=str(txin.txid)+str(txin.vout)+str(txin.scriptSig)
        for txout in tx.outputs:
            txdata+=str(txout.value)+str(txout.scriptPubKeyHash)
        txid=sha3_256(sha3_256(txdata.encode()).digest()).hexdigest()
        if tx.txid!=txid:
            print("REHASHED TXID MISMATCH")
            return False
        txids.append(txid)
    merkle=merkle_root_hash(txids)
    target=prevblock.target
    if (blockHeight+1)%50==0:
        target=calculate_new_target_hash(target,getTargetQuotent(blockHeight))
    blockData=f"{block.version}{prevblock.hash}{merkle}{totalTips}{block.timeStamp}{target}{len(block.transactions)}".encode()
    #blockData=f"{block.version}{block.previousBlock}{merkle}{totalTips}{block.timeStamp}{block.target}{len(block.transactions)}".encode()
    blockHash=sha3_256(sha3_256(blockData+str(block.nonce).encode()).digest()).hexdigest()
    if blockHash!=block.hash:
        print("BLOCKHASH FAIL")
        return False
    if blockHash==prevblock.hash:
      print("SAME BLOCKHASH DETECTED")
      return False
    for tx in block.transactions:
        for inp in tx.inputs:
            if not (inp.txid=="0000000000000000000000000000000000000000000000000000000000000000" and inp.vout==0 and inp.scriptSig=="coinbase"):
                if not databaseUtils.removeUTXO(inp.txid,inp.vout):
                    return False
    if not databaseUtils.addBlock(block,blockHeight+1):
        return False
    if not databaseUtils.addUTXOS(block.transactions,blockHeight+1):
        return False
    

"""
priv="37f25dcfbe828498996ce296e582ddf18bca5ff4d5eb505898e874e42d3694b1"
pub="048891b4684ca59f80279e6e2dd9e5c1cf6f2794731d7a84d6233ae188ba9b597b91bcaf674d2a3158d866313efd42eae41f8d09a834a56e51b513b3acc05fb1f1"

addr=generate_address(bytes.fromhex(pub))
vout=2
sk=ecdsa.SigningKey.from_string(bytes.fromhex(priv),curve=ecdsa.SECP256k1,hashfunc=sha3_256)
sig=sk.sign_digest(sha3_256(sha3_256((addr+str(vout)).encode()).digest()).digest()).hex()
inp=blockchain.input("bigballs",2,(pub+";"+sig))
print(checkUTXOUnlock(inp))"""

"""
action=input("Action: ")
if int(action)==1:
    candidateBlock=generateCanaditBlock("DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh").toJSON()
    f=open("candidate.txt","w")
    json.dump(candidateBlock,f)
    f.close()
elif int(action)==2:
    f=open("newblock.txt",'r')
    data=json.load(f)
    block=jsonToBlockDict(data)
    print(addBlock(block))
    candidateBlock=generateCanaditBlock("DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh").toJSON()
    f=open("candidate.txt","w")
    json.dump(candidateBlock,f)
    f.close()
elif int(action)==3:
    #ADD TRANSACTION
    txdata={'version': 0, 'txid': '0850f6d12b7167fda57454da3f8dcf45da06a6c2a583e6470ddb5f557bcff456', 'inputs': [{'txid': '10ca514c77d80cdbfee2ded1d702e2557f9671f46dd1c5b4ac768b68fc12de06', 'vout': 0, 'scriptSig': '04d15faa746e543da9a2b4f4dda9c4ccc7a2b461669436c3e547eeffcf4fa4b517ba4d34d02ac5ce5ec02eee10d9f541114b6a47f37e8d93c66f256bf999a82789;1c1e59d1af0719c059e83289b766d554006cf9f8626ad470ebaff428be08bf0a4673f24714fe744e9d94bf60fdf515b12a35f01dc060c41297c27ea8b603714e'}, {'txid': 'd4f5df0a7f160840c3ffed7121aaebec9a49fa48bf754007b7f43e0172f6f850', 'vout': 0, 'scriptSig': '04d15faa746e543da9a2b4f4dda9c4ccc7a2b461669436c3e547eeffcf4fa4b517ba4d34d02ac5ce5ec02eee10d9f541114b6a47f37e8d93c66f256bf999a82789;6b271846fc6230e82e80329a95cb117dbafa26bcfc4bd219482d086d8d0f0fc966610f7e300a9e82ac0f53605bce274ac98e279a83d6214917146613a0f107c7'}, {'txid': '79806538f1adae60ea65c11a7944be56822fb7d9d2af91992a1475e15320868b', 'vout': 1, 'scriptSig': '04d15faa746e543da9a2b4f4dda9c4ccc7a2b461669436c3e547eeffcf4fa4b517ba4d34d02ac5ce5ec02eee10d9f541114b6a47f37e8d93c66f256bf999a82789;e603ccc617f910f3ce6d3989c736532f606131471f19f671dc7046a2070ef14278de43e1aa13d96c03eb18e375e5a8b37b84864709792535e2d71f36b1281c77'}, {'txid': '79806538f1adae60ea65c11a7944be56822fb7d9d2af91992a1475e15320868b', 'vout': 4, 'scriptSig': '04d15faa746e543da9a2b4f4dda9c4ccc7a2b461669436c3e547eeffcf4fa4b517ba4d34d02ac5ce5ec02eee10d9f541114b6a47f37e8d93c66f256bf999a82789;6dd0b19266d324839ac0aa3ae7fce4ee7529e2c6557ab4b3357891561de579657f111b60d27400a38a256941714b3b64598107433c0be48dbb5f5461ef610e94'}, {'txid': '79806538f1adae60ea65c11a7944be56822fb7d9d2af91992a1475e15320868b', 'vout': 11, 'scriptSig': '04d15faa746e543da9a2b4f4dda9c4ccc7a2b461669436c3e547eeffcf4fa4b517ba4d34d02ac5ce5ec02eee10d9f541114b6a47f37e8d93c66f256bf999a82789;9e20883accca4f4be90bb842f91b770d1223485d58d45cc3c5a7f2b2a7d4e4bbfef58a9692d7fa1838cadffe62d0f8db966e325a39127f02484a3bae3ce37df4'}, {'txid': '79806538f1adae60ea65c11a7944be56822fb7d9d2af91992a1475e15320868b', 'vout': 9, 'scriptSig': '04d15faa746e543da9a2b4f4dda9c4ccc7a2b461669436c3e547eeffcf4fa4b517ba4d34d02ac5ce5ec02eee10d9f541114b6a47f37e8d93c66f256bf999a82789;d0af306da031fe31bd13462dc0f53395a71404a17752550420e0c024d23bc0c53f90855bebdc4cd9174e1516a0698f509f943f49b8dabd28ca32ff7b65360fd6'}], 'outputs': [{'value': 3, 'scriptPubKeyHash': 'DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh'}, {'value': 313212, 'scriptPubKeyHash': 'DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh'}, {'value': 1, 'scriptPubKeyHash': 'DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh'}, {'value': 21, 'scriptPubKeyHash': 'DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh'}], 'inputCount': 6, 'outputCount': 4, 'timeStamp': 1754385444.570634}
    tx=jsonToTransactionDict(txdata)
    print(newTransaction(tx))
    candidateBlock=generateCanaditBlock("DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh").toJSON()
    f=open("candidate.txt","w")
    json.dump(candidateBlock,f)
    f.close()
    pass
"""
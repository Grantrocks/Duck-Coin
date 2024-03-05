import hashlib
import json
import base58
import dbManager
import binascii
import ecdsa
# Classes

class MemoryPool:
    transactions=[]

class Block:
    header={
        "version":0,
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
    version=0
    inputCount=0
    inputs=[]
    outputCount=0
    lockTime=0

class Input:
    txid=""
    out=""
    scriptSig={"pubKey":"","signature":""}
class OutPut:
    value=0
    scriptPubKey=""



# Functions
def verifyTXOwnership(pubKey:str,signature:str,outputSelect:int,txID:str):
    transaction=dbManager.fetchTransaction(txID)
    if outputSelect>transaction['outputCount']:
        return False
    output=transaction['outputs'][outputSelect]
    OldPub=output['scriptPubKey']
    hashofPub = hashlib.sha3_256(binascii.unhexlify(pubKey)).hexdigest()
    ripeMDofhashOfPub = hashlib.new('ripemd160', binascii.unhexlify(hashofPub))
    prependNetworkByte = '17' + ripeMDofhashOfPub.hexdigest()
    hash = prependNetworkByte
    for x in range(1,3):
        hash = hashlib.sha3_256(binascii.unhexlify(hash)).hexdigest()
    cheksum = hash[:8]
    appendChecksum = prependNetworkByte + cheksum
    newOldPub = base58.b58encode(binascii.unhexlify(appendChecksum))
    if newOldPub!=OldPub:
        return False
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubKey[2:]), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha3_256)
    return vk.verify(bytes.fromhex(signature), txID.encode())

def createTransaction(pubKey:str,signature:str,recipient:str,outputSelect:int,txID:str,amount:int):
    if not verifyTXOwnership(pubKey,signature,outputSelect,txID):
        return 1

    inp=Input
    inp.out=outputSelect
    inp.txid=txID
    inp.scriptSig['pubKey']=pubKey
    inp.scriptSig['signature']=signature
    out=OutPut
    out.value=amount
    out.scriptPubKey=recipient


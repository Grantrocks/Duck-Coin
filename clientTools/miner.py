import hashlib
import json
block={'header': {'version': 0, 'height': 0, 'last_block_hash': '', 'merkle_root': '9c7edf4e021360ae19b2e5b1b265b31961dfdad25f67e5ab515171cfe3cda81e', 'time': 1709846538.68299, 'target': '0fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'}, 'transactions': [{'inputCount': 1, 'inputs': [{'txid': '', 'scriptSig': {'pubKey': 'COINBASE', 'signature': '2024 March 7 And Duino Coin is at risk of shutting down. Due to this I created this currency to try and replace it.'}}], 'outputCount': 1, 'outputs': [{'value': 500000000, 'scriptPubKey': 'ASpdmX74XUJwdxFdrJbBMb3j3vgswmLk9q'}], 'created': 1709846538.682729, 'locktime': 2, 'txid': '9c7edf4e021360ae19b2e5b1b265b31961dfdad25f67e5ab515171cfe3cda81e'}]}
print(block)
nonce=0
target=int("000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",16)
hash=0
while True:
    print(json.dumps(block['header'])+str(nonce))
    h1=hashlib.sha3_256(f"{json.dumps(block['header'])}{str(nonce)}".encode()).hexdigest()
    print(h1)
    h2=hashlib.sha3_256(h1.encode()).hexdigest()
    hash=int(h2,16)
    if hash<=target:
        break
    nonce+=1
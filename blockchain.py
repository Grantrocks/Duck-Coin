class block:
    def __init__(self,version:int,previousBlock:str,merkleRoot:str,timeStamp:float,target:str,transactionCount:int, transactions:list,tips:int,hash:str="",nonce:int=0):
        self.version = version
        self.previousBlock=previousBlock
        self.merkleRoot=merkleRoot
        self.tips=tips
        self.timeStamp=timeStamp
        self.hash=hash
        self.nonce=nonce
        self.target=target
        self.transactionCount=transactionCount
        self.transactions = transactions
    def toJSON(self):
        transactions=[]
        print(self.transactions)
        for tx in self.transactions:
            txINS=[]
            txOUTS=[]
            print(tx)
            for ins in tx.inputs:
                txINS.append(ins.toJSON())
            for outs in tx.outputs:
                txOUTS.append(outs.toJSON())
            transactions.append({"version":tx.version,"txid":tx.txid,"inputs":txINS,"outputs":txOUTS,"inputCount":tx.inputCount,"outputCount":tx.outputCount,"timeStamp":tx.timeStamp})
        return {"version":self.version,"previousBlock":self.previousBlock,"merkleRoot":self.merkleRoot,"tips":self.tips,"timeStamp":self.timeStamp,"hash":self.hash,"nonce":self.nonce,"target":self.target,"transactionCount":self.transactionCount,"transactions":transactions}
class transaction:
    def __init__(self,version:str,inputs:list,outputs:list,inputCount:int,outputCount:int,timeStamp:float,txid:str=""):
        self.inputs=inputs # The inputs of the transaction.
        self.txid=txid # The hash of the transaction. FILLED IN WHEN ADDED TO MEMPOOL
        self.outputs=outputs # The outputs of the transaction
        self.version=version # The version of the blockchain at the time of the transaction.    
        self.inputCount=inputCount # The amount of inputs being used in your transaction.
        self.outputCount=outputCount # The amount of outputs in your transaction.
        self.timeStamp=timeStamp # The time that your transaction was recived by the node.
    def toJSON(self):
        inps=[]
        outs=[]
        for tx in self.inputs:
            inps.append(tx.toJSON())
        for tx in self.outputs:
            outs.append(tx.toJSON())
        return {"version":self.version,"txid":self.txid,"inputs":inps,"outputs":outs,"inputCount":self.inputCount,"outputCount":self.outputCount,"timeStamp":self.timeStamp}
"""

To spend this output, you must provide a public key that hashes to this hash, and a signature matching that public key.

Basically you take the UTXO data and then you provide your public key and a signature of your
transaction data (version,txid,vout,) hashed.

If you dont spend all of your coins or specify a tip and you dont specify where to send the rest of your coins, if you dont use all the duckoshi unlocked, any leftover will be considered as a tip. Keep in mind you can send yourself duckoshi.

There is a required 2 duckoshi fee

If your tip is less than the remaning amount of coins after selecting outputs anything left over will be sent to the first inputs public key.

"""
class input:
    def __init__(self,txid:str,vout:int,scriptSig:str=""):
        if type(txid)!=str:
            raise TypeError("Argument txid must be a string.")
        if type(vout)!=int:
            raise TypeError("Argument vout must be a integer.")
        if type(scriptSig)!=str:
            raise TypeError("Argument scriptSig must be a string.")
        self.txid=txid # The transaction hash that your unlocking.
        self.vout=vout # The index (starting at 0) of the output to be spent from the TXID.
        self.scriptSig=scriptSig # The public key of the hashed pubkey from the UTXO and the signature of the hashed transaction data in the format. pubKey;signature
    def toJSON(self):
        return {"txid":self.txid,"vout":self.vout,"scriptSig":self.scriptSig}
class output:
    def __init__(self,value:int,scriptPubKeyHash:str):
        if type(value)!=int:
            raise TypeError("Argument value must be a integer.")
        if type(scriptPubKeyHash)!=str:
            raise TypeError("Argument scriptPubKeyHash must be a string.")
        self.value=value
        self.scriptPubKeyHash=scriptPubKeyHash
    def toJSON(self):
        return {"value":self.value,"scriptPubKeyHash":self.scriptPubKeyHash}
    
class coinbaseTransaction:
    def __init__(self,hashedPubKey:str,reward:int,version:int,timeStamp:float):
        self.version=version
        self.inputs=[input("0000000000000000000000000000000000000000000000000000000000000000",0,"coinbase")]
        self.inputCount=1
        self.outputs=[output(reward,hashedPubKey)]
        self.outputCount=1
        self.timeStamp=timeStamp
        self.txid=""
    def toJSON(self):
        inps=[]
        outs=[]
        for tx in self.inputs:
            inps.append(tx.toJSON())
        for tx in self.outputs:
            outs.append(tx.toJSON())
        return {"version":self.version,"inputs":inps,"outputs":outs,"inputCount":self.inputCount,"outputCount":self.outputCount,"timeStamp":self.timeStamp}
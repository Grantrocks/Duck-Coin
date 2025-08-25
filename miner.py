import threading
import time
from hashlib import sha3_256
import json
import datetime
#import winsound
import node
# =========================
# Configuration
# =========================
NUM_THREADS = 9        # How many threads to run
#block="{\"version\": 0, \"previousBlock\": \"Thedateis8/1/2025,imonvacationinhawaiiandjustafewdaysagotherewasatsunamithathitus.Wewerehikinginthemountainsandonthewaybackwegotabunchofwarningsaboutthetsunamionourphones.Itsenttheentireislandintocompletechaosandscaredeveryone.Crazyshit.\", \"merkleRoot\": \"12402ced31507a714e79047650c6d57ea0002b935015bf920f8cdac7f309cbce\", \"tips\": 0, \"timeStamp\": 1754120149.341011, \"hash\": \"00000dee7cfbca5f108df853ce978c80a69cf89f4a2335243a49c948cabb956d\", \"nonce\": 156250, \"target\": \"0000000f00000000000000000000000000000000000000000000000000000000\", \"transactionCount\": 1, \"transactions\": [{\"version\": 0, \"txid\": \"12402ced31507a714e79047650c6d57ea0002b935015bf920f8cdac7f309cbce\", \"inputs\": [{\"txid\": \"0000000000000000000000000000000000000000000000000000000000000000\", \"vout\": 0, \"scriptSig\": \"coinbase\"}], \"outputs\": [{\"value\": 3000000000, \"scriptPubKeyHash\": \"DBGoWEXyVbydE235VJYoYkvE3cMniJyobm\"}], \"inputCount\": 1, \"outputCount\": 1, \"timeStamp\": 1754120149.339984, \"tip\": 0}]}"
#f=open("candidate.txt","r")
#block=json.load(f)
#f.close()
# =========================
# Function each thread runs
# =========================
def worker_thread(thread_id:int,stop_mining,block):
    workerTimestamp=datetime.datetime.now().timestamp()
    blockData=f"{block['version']}{block['previousBlock']}{block['merkleRoot']}{block['tips']}{workerTimestamp}{block['target']}{block['transactionCount']}".encode()
    nonce=0
    target=int(block['target'],16)
    print(f"[Thread {thread_id}]: Started Mining | Target: {block['target']}")
    hash=0
    hashstr=""
    blockFound=False
    hashTerm=0
    prevTime=datetime.datetime.now().timestamp()
    while True:
        h1=sha3_256(blockData+str(nonce).encode()).digest()
        h2=sha3_256(h1).hexdigest()
        hashstr=h2
        hash=int(h2,16)
        if stop_mining.is_set():
            break
        if nonce%500000==0 and nonce!=0:
            diff=datetime.datetime.now().timestamp()-prevTime
            hashrate=hashTerm/diff
            prevTime=datetime.datetime.now().timestamp()
            hashTerm=0
            print(f"[Thread {thread_id}]: Mining at {round(hashrate)}h/s | Hash: {h2} | Nonce: {nonce}")
        if hash<=target:
            blockFound=True
            break
        nonce+=1
        hashTerm+=1
    if blockFound:
        block['hash']=hashstr
        block['timeStamp']=workerTimestamp
        block['nonce']=nonce
        f=open("newblock.txt","w")
        json.dump(block,f)
        f.close()
        print(f"[Thread {thread_id}]: Found Block: "+hashstr)
        print(f"[Thread {thread_id}]: Nonce: "+str(nonce))
        stop_mining.set()
        #winsound.Beep(331, 500)
        print(node.addBlock(node.jsonToBlockDict(block)))

# =========================
# Main
# =========================
stop_mining=threading.Event()

def main():
    while True:
        candidateBlock=node.generateCanaditBlock("DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh").toJSON()
        stop_mining.clear()
        threads = []
        for i in range(NUM_THREADS):
            t = threading.Thread(target=worker_thread, args=(i+1,stop_mining,candidateBlock))
            t.start()
            threads.append(t)
            time.sleep(0.3)
        # Wait for all threads to finish
        for t in threads:
            t.join()
if __name__ == "__main__":
    main()
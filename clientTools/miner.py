import hashlib
import json
import socket
HOST = "0.0.0.0"  # The server's hostname or IP address
PORT = 20000  # The port used by the server
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(b"getCandidateBlock,ANuF9s1wvhcR5SiGGedZNnaiXsdUUAt9eq")
data = s.recv(1024).decode()
block=json.loads(data)
print(block)
nonce=0
target=int(block['header']['target'],16)
hash=0
header=json.dumps(block['header'])
while True:
    h1=hashlib.sha3_256(f"{header}{str(nonce)}".encode()).hexdigest()
    h2=hashlib.sha3_256(h1.encode()).hexdigest()
    hash=int(h2,16)
    if hash<=target:
        break
    nonce+=1
print(hex(hash)[2:])
print(nonce)
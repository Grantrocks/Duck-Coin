import hashlib
import json
import socket
def convertBlockJSON(block):
  return f"{str(block['version'])}{str(block['height'])}{block['last_block_hash']}{block['merkle_root']}{str(block['time'])}{block['target']}"
HOST = "0.0.0.0"  # The server's hostname or IP address
PORT = 20021 # The port used by the server
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
while True:
  s.sendall(b"getCandidateBlock~ANuF9s1wvhcR5SiGGedZNnaiXsdUUAt9eq")
  data = s.recv(1024).decode()
  block=json.loads(data)
  print("Mining...")
  nonce=0
  target=int(block['header']['target'],16)
  hash=0
  header=block['header']
  hashstr=""
  print(convertBlockJSON(header))
  while True:
      h1=hashlib.sha3_256(f"{convertBlockJSON(header)}{str(nonce)}".encode()).hexdigest()
      h2=hashlib.sha3_256(h1.encode()).hexdigest()
      hashstr=h2
      hash=int(h2,16)
      if hash<=target:
          break
      nonce+=1
    
  block['header']['hash']=hashstr
  block['header']['nonce']=nonce
  print("Found Block: "+hashstr)
  s.sendall(("addBlock~"+json.dumps(block)+"~ANuF9s1wvhcR5SiGGedZNnaiXsdUUAt9eq").encode())
  data=s.recv(1024).decode()
  print(data)
import hashlib
import json
import socket
import datetime
def convertGBtoByte(size):
  gb = size * (1024 * 1024 * 1024)
  return gb
def convertBlockJSON(block):
  return f"{str(block['version'])}{str(block['height'])}{block['last_block_hash']}{block['merkle_root']}{str(block['time'])}{block['target']}"
def sendCommand(command):
  HOST = "raspberrypi.local"  # The server's hostname or IP address
  PORT = 20000 # The port used by the server
  s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  msg_bytes = command.encode()
  length_prefix = len(msg_bytes).to_bytes(4, 'big')
  s.sendall(length_prefix+msg_bytes)
  data=s.recv(convertGBtoByte(1)).decode()
  s.close()
  return data

address=input("Address: ")
while True:
  data = sendCommand("getCandidateBlock~"+address)
  block=json.loads(data)
  print(f"Mining: {convertBlockJSON(block['header'])}")
  nonce=0
  target=int(block['header']['target'],16)
  hash=0
  header=block['header']
  hashstr=""
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
  res=sendCommand("addBlock~"+json.dumps(block)+"~"+address)
  print(res)
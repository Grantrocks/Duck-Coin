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

#addBlock~{"header": {"version": 0, "height": 16, "last_block_hash": "000000329f2161a6f22f5e31bc9b17073a1fada4be470ee67e533de3a5df3b01", "merkle_root": "5dd23f493d20c2cd8071876e38e6a5f3ff4f937c510ff8691df8d6aca553e3c5", "time": 1751949285.165731, "target": "00000033fbf61fd23a6e00000000000000000000000000000000000000000000", "hash": "0000002181d0327177f4fca4faaba710ed29d6b41d38199779af8462f35a4762", "nonce": 29212258}, "transactions": [{"inputCount": 1, "inputs": [{"txid": "", "scriptSig": {"pubKey": "COINBASE", "signature": "waddle"}}], "outputCount": 1, "outputs": [{"value": 500000000, "scriptPubKey": "AXrUMwnoCTbkWuBDmsXjF3hKwtvCdAmTbM"}], "created": 1751949285.160502, "locktime": 18, "txid": "cb74f20cd74014ec1bfa87784cb60f184a2d8e3c604830c2e6def0186f3001e7"}, {"inputCount": 4, "inputs": [{"txid": "3210fbf17364153e4ecd88fb98068860f6fec493393e276944b28c0052c21141", "out": 0, "scriptSig": {"pubKey": "10f3ca1f374ae2acf31dc410ee27ed62d2e6edc41b8b932a0a6137baee706640f6912b1ed7d631e124777563f255ef83aeae4560513304e7c91a9d19bd389e5bf2", "signature": "463b99fbbe42b34ff461f0bfae4ea56b845c0f85c56b22b880ef996e421725e3f06796acd2f99298c80759e11007dea1e8573a517b0ad8d9d5864baaafc26c63"}}, {"txid": "14b6ed71c8850f07cb6c760a25c142592047715033afd3e437274cdc339c7807", "out": 0, "scriptSig": {"pubKey": "10f3ca1f374ae2acf31dc410ee27ed62d2e6edc41b8b932a0a6137baee706640f6912b1ed7d631e124777563f255ef83aeae4560513304e7c91a9d19bd389e5bf2", "signature": "463b99fbbe42b34ff461f0bfae4ea56b845c0f85c56b22b880ef996e421725e3f06796acd2f99298c80759e11007dea1e8573a517b0ad8d9d5864baaafc26c63"}}, {"txid": "30855b3a7f3f2e3fabdbd496ec8e06710e987b634c2048af74319e02c09aad48", "out": 0, "scriptSig": {"pubKey": "10f3ca1f374ae2acf31dc410ee27ed62d2e6edc41b8b932a0a6137baee706640f6912b1ed7d631e124777563f255ef83aeae4560513304e7c91a9d19bd389e5bf2", "signature": "463b99fbbe42b34ff461f0bfae4ea56b845c0f85c56b22b880ef996e421725e3f06796acd2f99298c80759e11007dea1e8573a517b0ad8d9d5864baaafc26c63"}}, {"txid": "e1abfdb31efe3f3fe1fb16e1196956f79e9951b7d2e91c1baf1f860bd3e5dccc", "out": 0, "scriptSig": {"pubKey": "10f3ca1f374ae2acf31dc410ee27ed62d2e6edc41b8b932a0a6137baee706640f6912b1ed7d631e124777563f255ef83aeae4560513304e7c91a9d19bd389e5bf2", "signature": "463b99fbbe42b34ff461f0bfae4ea56b845c0f85c56b22b880ef996e421725e3f06796acd2f99298c80759e11007dea1e8573a517b0ad8d9d5864baaafc26c63"}}], "outputCount": 1, "outputs": [{"value": 2000000000, "scriptPubKey": "AGvdsk4cxj61XGcCnzDG1A9SsQ26AyfCqm"}], "created": 1751868664.814989, "locktime": 17, "txid": "b4a4025a167e7b6c028ff48adb67d555d335a88c3b8dc46a36f55637790c5538"}], "dbIDS": ["d47bfc28a1732fe5ceb3a543fa1a87f1adb93fc6"]}~AXrUMwnoCTbkWuBDmsXjF3hKwtvCdAmTbM
res=sendCommand('addBlock~{"header": {"version": 0, "height": 16, "last_block_hash": "000000329f2161a6f22f5e31bc9b17073a1fada4be470ee67e533de3a5df3b01", "merkle_root": "5dd23f493d20c2cd8071876e38e6a5f3ff4f937c510ff8691df8d6aca553e3c5", "time": 1751949285.165731, "target": "00000033fbf61fd23a6e00000000000000000000000000000000000000000000", "hash": "0000002181d0327177f4fca4faaba710ed29d6b41d38199779af8462f35a4762", "nonce": 29212258}, "transactions": [{"inputCount": 1, "inputs": [{"txid": "", "scriptSig": {"pubKey": "COINBASE", "signature": "waddle"}}], "outputCount": 1, "outputs": [{"value": 500000000, "scriptPubKey": "AXrUMwnoCTbkWuBDmsXjF3hKwtvCdAmTbM"}], "created": 1751949285.160502, "locktime": 18, "txid": "cb74f20cd74014ec1bfa87784cb60f184a2d8e3c604830c2e6def0186f3001e7"}, {"inputCount": 4, "inputs": [{"txid": "3210fbf17364153e4ecd88fb98068860f6fec493393e276944b28c0052c21141", "out": 0, "scriptSig": {"pubKey": "10f3ca1f374ae2acf31dc410ee27ed62d2e6edc41b8b932a0a6137baee706640f6912b1ed7d631e124777563f255ef83aeae4560513304e7c91a9d19bd389e5bf2", "signature": "463b99fbbe42b34ff461f0bfae4ea56b845c0f85c56b22b880ef996e421725e3f06796acd2f99298c80759e11007dea1e8573a517b0ad8d9d5864baaafc26c63"}}, {"txid": "14b6ed71c8850f07cb6c760a25c142592047715033afd3e437274cdc339c7807", "out": 0, "scriptSig": {"pubKey": "10f3ca1f374ae2acf31dc410ee27ed62d2e6edc41b8b932a0a6137baee706640f6912b1ed7d631e124777563f255ef83aeae4560513304e7c91a9d19bd389e5bf2", "signature": "463b99fbbe42b34ff461f0bfae4ea56b845c0f85c56b22b880ef996e421725e3f06796acd2f99298c80759e11007dea1e8573a517b0ad8d9d5864baaafc26c63"}}, {"txid": "30855b3a7f3f2e3fabdbd496ec8e06710e987b634c2048af74319e02c09aad48", "out": 0, "scriptSig": {"pubKey": "10f3ca1f374ae2acf31dc410ee27ed62d2e6edc41b8b932a0a6137baee706640f6912b1ed7d631e124777563f255ef83aeae4560513304e7c91a9d19bd389e5bf2", "signature": "463b99fbbe42b34ff461f0bfae4ea56b845c0f85c56b22b880ef996e421725e3f06796acd2f99298c80759e11007dea1e8573a517b0ad8d9d5864baaafc26c63"}}, {"txid": "e1abfdb31efe3f3fe1fb16e1196956f79e9951b7d2e91c1baf1f860bd3e5dccc", "out": 0, "scriptSig": {"pubKey": "10f3ca1f374ae2acf31dc410ee27ed62d2e6edc41b8b932a0a6137baee706640f6912b1ed7d631e124777563f255ef83aeae4560513304e7c91a9d19bd389e5bf2", "signature": "463b99fbbe42b34ff461f0bfae4ea56b845c0f85c56b22b880ef996e421725e3f06796acd2f99298c80759e11007dea1e8573a517b0ad8d9d5864baaafc26c63"}}], "outputCount": 1, "outputs": [{"value": 2000000000, "scriptPubKey": "AGvdsk4cxj61XGcCnzDG1A9SsQ26AyfCqm"}], "created": 1751868664.814989, "locktime": 17, "txid": "b4a4025a167e7b6c028ff48adb67d555d335a88c3b8dc46a36f55637790c5538"}], "dbIDS": ["d47bfc28a1732fe5ceb3a543fa1a87f1adb93fc6"]}~AXrUMwnoCTbkWuBDmsXjF3hKwtvCdAmTbM')
print(res)
#address=input("Address: ")
#while True:
  #data = sendCommand("getCandidateBlock~"+address)
  #block=json.loads(data)
  #print(f"Mining: {convertBlockJSON(block['header'])}")
  #nonce=0
  #target=int(block['header']['target'],16)
  #hash=0
  #header=block['header']
  #hashstr=""
  #while True:
      #h1=hashlib.sha3_256(f"{convertBlockJSON(header)}{str(nonce)}".encode()).hexdigest()
      #h2=hashlib.sha3_256(h1.encode()).hexdigest()
      #hashstr=h2
      #hash=int(h2,16)
      #if hash<=target:
          #break
      #nonce+=1
  #block['header']['hash']=hashstr
  #block['header']['nonce']=nonce
  #print("Found Block: "+hashstr)
  #print("")
  #print("addBlock~"+json.dumps(block)+"~"+address)
  #res=sendCommand("addBlock~"+json.dumps(block)+"~"+address)
  #print(res)
  #print()
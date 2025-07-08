import socket
import hashlib
import json
from _thread import *
import threading
import blockchain
import dbManager
import ast
import signal
import sys

def convertGBtoByte(size):
  gb = size * (1024 * 1024 * 1024)
  return gb


def recv_all(sock, n):
    """Read exactly n bytes from the socket."""
    data = b''
    while len(data) < n:
        part = sock.recv(n - len(data))
        if not part:
            raise ConnectionError("Socket closed before receiving expected data")
        data += part
    return data

def recv_with_length(sock):
    # Step 1: Get the 4-byte length header
    raw_length = recv_all(sock, 4)
    message_length = int.from_bytes(raw_length, 'big')

    # Step 2: Receive the full message
    return recv_all(sock, message_length)


# thread function
def threaded(c):
  while True:
    try:
       data = recv_with_length(c)
       print(data.decode())  # or parse it if it's JSON, etc.
    except ConnectionError as e:
       print(f"Error: {e}")
       c.close()
       break
    print(data)
    print()
    data=data.decode().split("~")
    # Handle Messages from client
    print(data)
    print()
    cmd=data[0]
    if cmd=="PING":
      # Command: PING
      c.send("PONG".encode())
    elif cmd=="fetchBlock":
      # Command: fetchBlock, BlockHash
      block=dbManager.fetchBlockData(data[1])
      block={"header":json.loads(block[2]),"transactions":json.loads(block[3])}
      c.send(json.dumps(block).encode())
    elif cmd=="fetchTransaction":
      # Command: fetchTransaction, TXID
      tx=dbManager.fetchTransaction(data[1])
      c.send(json.dumps(tx).encode())
    elif cmd=="getTransactionsByPubKey":
      # Command: getTransactionsByPubKey, PubKey
      tx=dbManager.fetchTransactionsByPubKey(data[1],blockchain.generateAddressFromPubkey(data[1]))
      c.send(json.dumps(tx).encode())
    elif cmd=="createTransaction":
      # Command: createTransaction, pubKey (senders public key), recipient(reciver hashed pubkey), SigTX(["signature","txID",outputSelect]), amount (amount to send in quacks)
      tx=blockchain.createTransaction(data[1],data[2],ast.literal_eval(data[3]),int(data[4]))
      if type(tx)==type(0):
        c.send(json.dumps({"err":tx}).encode())
      else:
        c.send(json.dumps({"err":0}).encode())
    elif cmd=="getCandidateBlock":
      #Command: getCandidateBlock, creator (your address)
      block=json.dumps(blockchain.createBlock(data[1]))
      print(block)
      c.send(block.encode())
    elif cmd=="addBlock":
      # Command: addBlock, hash, nonce, nextBlockCreator
      print(data[1])
      block=json.loads(data[1])
      print("")
      print(block)
      nextBlockCreator=data[2]
      added=blockchain.addBlock(block,nextBlockCreator)
      if not added:
        c.send("INVALID".encode())
      c.send("VALID".encode())
    elif cmd=="getBalance":
      # Command: getBalance, pubkey
      balance=blockchain.getBalance(data[1])
      return c.send(str(balance).encode())
    else:
      c.send("Please specify a command".encode())
  c.close()
def signal_handler(sig, frame):
  print('You pressed Ctrl+C!')
  s.close()
  sys.exit(0)

def Main():
  host = "0.0.0.0"
  port = 20000 # Specify which port to open
  global s
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((host, port))
  s.listen(5)
  print(f"[SERVER] Listening on {(host, port)}")
  signal.signal(signal.SIGINT, signal_handler)
  while True:

    c, addr = s.accept()

    print('[SERVER] Connected to :', addr[0], ':', addr[1])

    start_new_thread(threaded, (c,))

if __name__ == '__main__':
  Main()

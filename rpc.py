import socket
import hashlib
import json
from _thread import *
import threading
import blockchain
import dbManager
import ast

def convertGBtoByte(size):
  gb = size * (1024 * 1024 * 1024)
  return gb
# thread function
def threaded(c):
  while True:
    data = c.recv(convertGBtoByte(1))
    if not data:
      print('Closed Connection')
      break
    data=data.decode().split("~")
    # Handle Messages from client
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
      c.send(block.encode())
    elif cmd=="addBlock":
      # Command: addBlock, hash, nonce, nextBlockCreator
      block=json.loads(data[1])
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


def Main():
  host = ""
  port = 20024 # Specify which port to open
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((host, port))
  print("socket binded to port", port)

  s.listen(5)
  print("socket is listening")

  while True:

    c, addr = s.accept()

    print('Connected to :', addr[0], ':', addr[1])

    start_new_thread(threaded, (c,))
  s.close()


if __name__ == '__main__':
  Main()

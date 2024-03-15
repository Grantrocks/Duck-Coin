
# Duck Coin

A simple, easy to use, cryptocurrency built around SHA3-256. Duck Coin was originally made to replace a currency known as Duino Coin (because of the message that said it was likely going to shut down), but since then has evolved into its own little system and community. 

## Getting Started

Duck Coin is super simple to use. Make sure you have python installed and then navigate to the directory that Duck Coin is in and run the commandd

# Duck Coin

A simple, easy to use, cryptocurrency built around SHA3-256. Duck Coin was originally made to replace a currency known as Duino Coin (because of the message that said it was likely going to shut down), but since then has evolved into its own little system and community. This is a PoW coin so mining is required. 

## Getting Started

Duck Coin is super simple to use. Make sure you have python installed and then navigate to the directory that Duck Coin is in and run the commands:

```
pip install -r requirements.txt
python rpc.py
```
This will launch a Duck Coin node to the following address and port 127.0.0.1:20000
To change these simply open up rpc.py scroll down to Main() and change it. Make sure you have the port forwarded to the public in your router and windows settings or else people wont be able to connect to your node unless you connect to theirs.

## Mining

The miner is super easy to use. Simply just run the command from the root directory of Duck Coin:
```
cd clientTools && python miner.py
```
The miner will then prompt your for your address which you can enter and it will start mining (on the assumption that the node the miner is set to is online, i recommed using your own as thats what its set to). Unless you connect the miner to a pool, the default node will solo mine only granting rewards if you find a block.
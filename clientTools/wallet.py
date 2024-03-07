import ecdsa
import binascii
import hashlib
import base58
import os
import codecs
import json
class Wallet:
    pk=None
    pub=None
    addr=None
    options={}
def generateWallet():
    ecdsaPrivateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1,hashfunc=hashlib.sha3_256)
    pk=ecdsaPrivateKey.to_string().hex()
    return pk

#SIGNING pk.sign(b"asdfasdfasdfasdfasdfasdfasdfasdf").hex()

def loadWallet(pk):
    pk=ecdsa.SigningKey.from_string(bytes().fromhex(pk),curve=ecdsa.SECP256k1,hashfunc=hashlib.sha3_256)
    ecdsaPublicKey = "10" +pk.get_verifying_key().to_string().hex()

    hash256FromECDSAPublicKey = hashlib.sha3_256(binascii.unhexlify(ecdsaPublicKey)).hexdigest()
    ridemp160FromHash256 = hashlib.new('ripemd160', binascii.unhexlify(hash256FromECDSAPublicKey))
    prependNetworkByte = '17' + ridemp160FromHash256.hexdigest()
    hash = prependNetworkByte
    for x in range(1,3):
        hash = hashlib.sha3_256(binascii.unhexlify(hash)).hexdigest()
    cheksum = hash[:8]
    appendChecksum = prependNetworkByte + cheksum
    bitcoinAddress = base58.b58encode(binascii.unhexlify(appendChecksum))
    addr=bitcoinAddress.decode('utf8')
    return [ecdsaPublicKey,addr]


def inWallet(walletClass):
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        print("Duck Coin Wallet V1.0")
        print("")
        print("Dasboard")
        print("Enter a command to do something")
        command=input("-->").lower()
        os.system('cls' if os.name == 'nt' else 'clear')
        if command=="help":
            print("Commands")
            print("DETAILS - PRINTS WALLET DETAILS SUCH AS PUBKEY AND ADDRESS")
        elif command=="details":
            print("Address: "+walletClass.addr)
            print("Public Key: "+wallet.pub)
while True:
    print("Duck Coin Wallet V1.0")
    print()
    print("This wallet is where you manage your coins.")
    print("1: Open Wallet")
    print("2: Generate New Wallet")
    command=input("-->")
    if command=="1":
        pk=input("Please Enter Private Key: ")
        wallet=Wallet
        tempDetails=loadWallet(pk)
        wallet.pk=pk
        wallet.pub=tempDetails[0]
        wallet.addr=tempDetails[1]
        inWallet(wallet)
    elif command=="2":
        pk=generateWallet()
        print("STORE THE FOLLOWING KEY. KEEP IT IN A SAFE PLACE. IF IT GETS LOST YOU WILL NO LONGER HAVE ACCESS TO YOUR WALLET. IF IT GETS STOLEN WELL THERE GOES YOUR COINS. IT WILL BE ONLY SHOWN ONCE!")
        input("ENTER TO CONTINUE")
        print()
        print(pk)
        print()
        input()
        tempDetails=loadWallet(pk)
        wallet=Wallet
        wallet.pk=pk
        wallet.pub=tempDetails[0]
        wallet.addr=tempDetails[1]
        inWallet(wallet)
    os.system('cls' if os.name == 'nt' else 'clear')


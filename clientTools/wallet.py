import ecdsa
import binascii
import hashlib
import base58
ecdsaPrivateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1,hashfunc=hashlib.sha3_256)

pk=ecdsaPrivateKey.to_string().hex()
print("Sig: "+ecdsaPrivateKey.sign(b"asdfasdfasdfasdfasdfasdfasdfasdf").hex())
ecdsaPublicKey = "10" +ecdsaPrivateKey.get_verifying_key().to_string().hex()
print("Pub: "+ecdsaPublicKey)

hash256FromECDSAPublicKey = hashlib.sha3_256(binascii.unhexlify(ecdsaPublicKey)).hexdigest()
ridemp160FromHash256 = hashlib.new('ripemd160', binascii.unhexlify(hash256FromECDSAPublicKey))
prependNetworkByte = '17' + ridemp160FromHash256.hexdigest()
hash = prependNetworkByte
for x in range(1,3):
    hash = hashlib.sha3_256(binascii.unhexlify(hash)).hexdigest()
cheksum = hash[:8]
appendChecksum = prependNetworkByte + cheksum
bitcoinAddress = base58.b58encode(binascii.unhexlify(appendChecksum))
print("Bitcoin Address: ", bitcoinAddress.decode('utf8'))
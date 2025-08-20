from hashlib import sha3_256
import ecdsa
import blockchain
from datetime import datetime
def base58_encode(data: bytes):
    """Encode bytes to a Base58 string."""
    # Convert big-endian bytes to integer
    num = int.from_bytes(data, byteorder='big')
    encode = ''
    while num > 0:
        num, rem = divmod(num, 58)
        encode = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'[rem] + encode
    # Add '1' for each leading 0 byte
    for byte in data:
        if byte == 0:
            encode = '1' + encode
        else:
            break
    return encode


def base58_check_encode(payload: bytes):
    """Encode payload with Base58Check: payload + checksum (4 bytes of double-SHA256)."""
    checksum = sha3_256(sha3_256(payload).digest()).digest()[:4]
    return base58_encode(payload + checksum)


def generate_keypair():
    """
    Generate ECDSA SECP256k1 key pair.
    Returns (private_key_bytes, public_key_bytes_uncompressed).
    """
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1,hashfunc=sha3_256)
    vk = sk.verifying_key
    private_key = sk.to_string()
    public_key = b'\x04' + vk.to_string()  # uncompressed format prefix 0x04
    return private_key.hex(), public_key.hex()

def generate_address(public_key: bytes):
    """
    Generate address:
    - Hash public key with SHA3-256.
    - Truncate hash to 20 bytes (like RIPEMD160).
    - Prepend version byte (0x1E for addresses starting with 'D').
    - Base58Check encode.
    """
    sha3_hash = sha3_256(public_key).digest()
    pubkey_hash_20 = sha3_hash[:20]
    version_byte = b'\x1E'  # Decimal 30, prefix 'D'
    payload = version_byte + pubkey_hash_20
    address = base58_check_encode(payload)
    return address

priv="e56a958a68860561c3ca01f6c1c41d6c5e9395aa1c3a6fbbc30ac001842f688a"
pub="04d15faa746e543da9a2b4f4dda9c4ccc7a2b461669436c3e547eeffcf4fa4b517ba4d34d02ac5ce5ec02eee10d9f541114b6a47f37e8d93c66f256bf999a82789"

addr=generate_address(bytes.fromhex(pub))
sk=ecdsa.SigningKey.from_string(bytes.fromhex(priv),curve=ecdsa.SECP256k1,hashfunc=sha3_256)
inp=[blockchain.input("10ca514c77d80cdbfee2ded1d702e2557f9671f46dd1c5b4ac768b68fc12de06",0),blockchain.input("d4f5df0a7f160840c3ffed7121aaebec9a49fa48bf754007b7f43e0172f6f850",0),blockchain.input("79806538f1adae60ea65c11a7944be56822fb7d9d2af91992a1475e15320868b",1),blockchain.input("79806538f1adae60ea65c11a7944be56822fb7d9d2af91992a1475e15320868b",4),blockchain.input("79806538f1adae60ea65c11a7944be56822fb7d9d2af91992a1475e15320868b",11),blockchain.input("79806538f1adae60ea65c11a7944be56822fb7d9d2af91992a1475e15320868b",9)]
out=[blockchain.output(3,"DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh"),blockchain.output(313212,"DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh"),blockchain.output(1,"DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh"),blockchain.output(21,"DE2U2MvKzMJJzXcHDbkyKSJextcvabBpQh")]
t=blockchain.transaction(version=0,inputs=inp,outputs=out,outputCount=len(out),inputCount=len(inp),timeStamp=datetime.now().timestamp())
txdata=str(t.version)+str(t.inputCount)+str(t.outputCount)+str(t.timeStamp)
for tx in t.inputs:
    txdata+=str(tx.txid)+str(tx.vout)
for tx in t.outputs:
    txdata+=str(tx.value)+str(tx.scriptPubKeyHash)
for inp in range(0,len(t.inputs)):
    t.inputs[inp].scriptSig=pub+";"+sk.sign_digest(sha3_256(sha3_256(txdata.encode()).digest()).digest()).hex()
txdata=str(t.version)+str(t.inputCount)+str(t.outputCount)+str(t.timeStamp)
for tx in t.inputs:
    txdata+=str(tx.txid)+str(tx.vout)+str(tx.scriptSig)
for tx in t.outputs:
    txdata+=str(tx.value)+str(tx.scriptPubKeyHash)
t.txid=sha3_256(sha3_256(txdata.encode()).digest()).hexdigest()
print(t.toJSON())
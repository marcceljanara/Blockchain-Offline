from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64

# Constants
KEY_SIZE = 32  # 256-bit key
IV_SIZE = 16   # 128-bit IV

# Passphrase
passphrase = 'XiFUvRHM5FN8Qk8vIDngNJezQ0vvxh5n'

def encrypt(plaintext, passphrase):
    # Ensure the key is 256 bits
    key = passphrase.encode('utf-8')[:KEY_SIZE]
    key = key.ljust(KEY_SIZE, b'\0')
    
    # Generate a random IV
    iv = get_random_bytes(IV_SIZE)
    
    # Create cipher object and encrypt the plaintext
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    
    # Encode the IV and encrypted message in Base64
    result = base64.b64encode(iv + encrypted).decode('utf-8')
    
    return result

# Example usage
plaintext = 'https://ipfs.xsmartagrichain.com/ipfs/bafybeidzx3omyo2d5buvfbvlekn6gczejo26xgxa7rxb5x6tv5q66vegcm'
encrypted_text = encrypt(plaintext, passphrase)
print('Encrypted text:', encrypted_text)

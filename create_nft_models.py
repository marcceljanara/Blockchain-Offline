import os
import time
from pathlib import Path
from dotenv import load_dotenv
from iota_sdk import MintNftParams, Wallet, utf8_to_hex
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import base64
import ipfsApi
import json

load_dotenv()

# Inisialisasi IPFS client
api = ipfsApi.Client('http://93.127.185.37', 5001)

# Constants for AES encryption
KEY_SIZE = 32  # 256-bit key
IV_SIZE = 16   # 128-bit IV

def upload_file(file_path):
    try:
        # Membaca file dari sistem file dan mengunggah ke IPFS
        result = api.add(file_path)
        cid_base58 = result['Hash']
        return cid_base58
    except Exception as e:
        print(f'Error mengunggah file ke IPFS: {e}')
        raise

def encrypt_uri(uri, passphrase):
    # Ensure the key is 256 bits
    key = passphrase.encode('utf-8')[:KEY_SIZE]
    key = key.ljust(KEY_SIZE, b'\0')
    
    # Generate a random IV
    iv = get_random_bytes(IV_SIZE)
    
    # Create cipher object and encrypt the plaintext
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(uri.encode(), AES.block_size))
    
    # Encode the IV and encrypted message in Base64
    result = base64.b64encode(iv + encrypted).decode('utf-8')
    
    return result

def mint_nft_and_delete_file(file_path, file, account, sender_address, passphrase):
    try:
        cid_base58 = upload_file(file_path)

        # Enkripsi URI
        encrypted_uri = encrypt_uri(f'https://ipfs.xsmartagrichain.com/ipfs/{cid_base58}', passphrase)

        # Membuat metadata untuk NFT
        metadata_object = {
            "id": os.urandom(10).hex(),
            "standard": "IRC27",
            "type": "application/x-hdf5",
            "version": "v1.0",
            "name": file,
            "uri": encrypted_uri,
        }

        metadata_bytes = utf8_to_hex(json.dumps(metadata_object))

        # Persiapan mint NFT
        params = MintNftParams(
            sender=sender_address,
            metadata=metadata_bytes,
            tag=utf8_to_hex("TEST NFT LRS"),
            issuer=sender_address,
            immutableMetadata=metadata_bytes,
        )

        transaction = account.mint_nfts([params])
        print(f'Transaction sent for file {file}: {os.environ["EXPLORER_URL"]}/block/{transaction.blockId}')

        # Menghapus file dari folder
        os.remove(file_path)
    except Exception as e:
        print(f'Error minting NFT for file {file}: {e}')
        raise

def process_file(file_path, file, account, sender_address, passphrase):
    while True:
        try:
            mint_nft_and_delete_file(file_path, file, account, sender_address, passphrase)
            # print(f'Successfully processed file: {file}')
            break
        except Exception as e:
            if 'address owns insufficient funds' in str(e):
                print('Queue...')
                account.sync()
            else:
                print(f'Error: {e}')
                account.sync()
                time.sleep(5)

def run():
    # Load environment variables
    password = os.environ['STRONGHOLD_PASSWORD']
    account_name = os.environ['ACCOUNT_NAME']
    passphrase = os.environ['AES_KEY']
    folder_path = './dataset-models'  # Adjust path to your dataset folder

    # Initialize the wallet
    wallet = Wallet(f'./{account_name}-database')

    # Set Stronghold password
    wallet.set_stronghold_password(password)

    # Get the account from the wallet
    account = wallet.get_account(account_name)

    # Sync account with the node
    account.sync()

    # Get the sender's address
    sender_address = account.addresses()[0].address

    processed_files = set()

    while True:
        try:
            # Get the list of files in the folder
            files = list(Path(folder_path).iterdir())
            new_files = [file for file in files if file.name not in processed_files]

            if new_files:
                for file in new_files:
                    file_path = str(file)
                    process_file(file_path, file.name, account, sender_address, passphrase)
                    processed_files.add(file.name)

                print("All new files processed!")
            else:
                print("No new files. Waiting for new files...")

        except Exception as e:
            print(f"Error during file processing: {e}")

        # Wait before checking the folder again
        time.sleep(60)

run()

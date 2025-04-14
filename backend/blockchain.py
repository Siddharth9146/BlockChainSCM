from web3 import Web3
import json
from dotenv import dotenv_values
import os

# Load environment variables
config = dotenv_values("../.env")
PROVIDER_URL = config.get("PROVIDER_URL", "http://127.0.0.1:7545")
CONTRACT_ADDRESS = config.get("CONTRACT_ADDRESS")
PRIVATE_KEY = config.get("PRIVATE_KEY")

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(PROVIDER_URL))

# Check if connected to Ethereum node
def is_connected():
    return w3.is_connected()

# Load contract ABI
def load_contract():
    # Path to contract JSON file (compiled contract)
    contract_path = os.path.join(os.path.dirname(__file__), "..", "contracts", "SupplyChain.json")
    
    try:
        with open(contract_path, 'r') as file:
            contract_json = json.load(file)
            
        # Get ABI
        abi = contract_json["abi"]
        
        # Get contract address from JSON if not in env
        networks = contract_json.get("networks", {})
        network_id = list(networks.keys())[0] if networks else None
        address = networks.get(network_id, {}).get("address", CONTRACT_ADDRESS) if network_id else CONTRACT_ADDRESS
        
        if not address:
            raise ValueError("Contract address not available")
            
        # Create contract instance
        contract = w3.eth.contract(address=address, abi=abi)
        return contract
    
    except Exception as e:
        print(f"Error loading contract: {e}")
        return None

# Get account address from private key
def get_account():
    if not PRIVATE_KEY:
        # If no private key, use the first account from Ganache
        return w3.eth.accounts[0]
    
    # Create account from private key
    account = w3.eth.account.from_key(PRIVATE_KEY)
    return account.address

# Add a product to the blockchain
def add_product(product_id, name, owner):
    try:
        contract = load_contract()
        if not contract:
            return None, "Contract not loaded"
            
        account = get_account()
        
        # Build transaction
        tx = contract.functions.addProduct(
            product_id,
            name,
            owner
        ).build_transaction({
            'from': account,
            'nonce': w3.eth.get_transaction_count(account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        if PRIVATE_KEY:
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        else:
            tx_hash = contract.functions.addProduct(
                product_id, 
                name, 
                owner
            ).transact({'from': account})
        
        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.transactionHash.hex(), None
    
    except Exception as e:
        return None, str(e)

# Transfer product ownership
def transfer_product(product_id, new_owner, new_status):
    try:
        contract = load_contract()
        if not contract:
            return None, "Contract not loaded"
            
        account = get_account()
        
        # Build transaction
        tx = contract.functions.transferProduct(
            product_id,
            new_owner,
            new_status
        ).build_transaction({
            'from': account,
            'nonce': w3.eth.get_transaction_count(account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        if PRIVATE_KEY:
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        else:
            tx_hash = contract.functions.transferProduct(
                product_id, 
                new_owner, 
                new_status
            ).transact({'from': account})
        
        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.transactionHash.hex(), None
    
    except Exception as e:
        return None, str(e)

# Update product status
def update_product_status(product_id, new_status):
    try:
        contract = load_contract()
        if not contract:
            return None, "Contract not loaded"
            
        account = get_account()
        
        # Build transaction
        tx = contract.functions.updateProductStatus(
            product_id,
            new_status
        ).build_transaction({
            'from': account,
            'nonce': w3.eth.get_transaction_count(account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        if PRIVATE_KEY:
            signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        else:
            tx_hash = contract.functions.updateProductStatus(
                product_id, 
                new_status
            ).transact({'from': account})
        
        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.transactionHash.hex(), None
    
    except Exception as e:
        return None, str(e)

# Get product details from blockchain
def get_product(product_id):
    try:
        contract = load_contract()
        if not contract:
            return None, "Contract not loaded"
        
        product = contract.functions.getProduct(product_id).call()
        
        # Get product history
        history_count = contract.functions.getProductHistoryCount(product_id).call()
        history = []
        
        for i in range(history_count):
            tx = contract.functions.getProductHistoryItem(product_id, i).call()
            history.append({
                "fromOwner": tx[0],
                "toOwner": tx[1],
                "action": tx[2],
                "status": tx[3],
                "timestamp": tx[4]
            })
        
        result = {
            "productId": product[0],
            "name": product[1],
            "currentOwner": product[2],
            "status": product[3],
            "createdAt": product[4],
            "updatedAt": product[5],
            "history": history
        }
        
        return result, None
    
    except Exception as e:
        return None, str(e)
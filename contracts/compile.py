#!/usr/bin/env python3
import json
import os
import sys
from web3 import Web3
from solcx import compile_standard, install_solc

# Install specific solc version
install_solc("0.8.0")

def compile_contract():
    # Read the Solidity contract
    with open("SupplyChain.sol", "r") as file:
        supply_chain_file = file.read()
    
    # Compile the contract
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SupplyChain.sol": {"content": supply_chain_file}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version="0.8.0",
    )

    # Save the compiled contract
    with open("SupplyChain.json", "w") as file:
        json.dump(compiled_sol, file)
    
    return compiled_sol


# Deply contract
from dotenv import load_dotenv

# Load .env from the root directory
load_dotenv(dotenv_path=".env")

def deploy_contract(compiled_sol):
    # Get bytecode
    bytecode = compiled_sol["contracts"]["SupplyChain.sol"]["SupplyChain"]["evm"]["bytecode"]["object"]
    
    # Get ABI
    abi = compiled_sol["contracts"]["SupplyChain.sol"]["SupplyChain"]["abi"]
    
    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    chain_id = 1337
    
    # # Get deployer account
    # my_address = w3.eth.accounts[0]
    # private_key = os.getenv("PRIVATE_KEY")  # Loaded from .env
    
    # if not private_key:
    #     raise ValueError("PRIVATE_KEY not found in .env file")

    private_key = "0x7a1b3777477ab87082be705bd915586441e8e24fad47fc6e1ccce287de343958"
    my_address = "0xd9aeF1212d4543c1e383f4264699D87BCc9C3E86"  # Replace with your address

    # Create contract instance
    SupplyChain = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Get latest transaction count
    nonce = w3.eth.get_transaction_count(my_address)
    
    # Build and sign transaction
    transaction = SupplyChain.constructor().build_transaction(
        {
            "chainId": chain_id,
            "from": my_address,
            "nonce": nonce,
            "gasPrice": w3.eth.gas_price,
        }
    )
    
    # Sign and send transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    # Wait for transaction receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Create deployment info for later use
    deployment_info = {
        "abi": abi,
        "networks": {
            "5777": {
                "address": tx_receipt.contractAddress,
                "transactionHash": tx_hash.hex()
            }
        }
    }
    
    # Save the deployment info
    os.makedirs("contracts", exist_ok=True)
    with open("contracts/SupplyChain.json", "w") as file:
        json.dump(deployment_info, file)
    
    return tx_receipt.contractAddress

if __name__ == "__main__":
    print("Compiling the contract...")
    compiled_sol = compile_contract()

    print("Deploying the contract...")
    contract_address = deploy_contract(compiled_sol)

    print(f"Contract deployed at: {contract_address}")
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


import json
import os
from web3 import Web3
from solcx import compile_source, install_solc

# Setup
install_solc("0.8.0")

ganache_url = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))
#connect to ganache

w3.eth.default_account = w3.eth.accounts[0]
#Zeroth account in ganache is used as default account here

# File paths
#first one is sol file path
#second one is deployment path
sol_path = r"C:\Users\lenovo\PycharmProjects\safeshare\contract\PostRecords.Sol"
deploy_info_path = r"C:\Users\lenovo\PycharmProjects\safeshare\contract\deployed.json"

# Read the smart contract file in readonly  mode
with open(sol_path, "r") as file:
    contract_source = file.read()

compiled_sol = compile_source(contract_source, solc_version="0.8.0")
#compiles it using solcx to generate:


contract_interface = compiled_sol['<stdin>:PostRecords']
#Solidity compilers label the compiled contract as <stdin>:ContractName.


print(contract_interface)

# Check if already deployed
if os.path.exists(deploy_info_path):
    # Load contract from file
    with open(deploy_info_path, "r") as f:
        deploy_data = json.load(f)
    contract_address = deploy_data["address"]
    abi = deploy_data["abi"]
    #ABI stands for  (Application Binary Interface)



    contract = w3.eth.contract(address=contract_address, abi=abi)
    print("✔ Contract loaded from existing deployment:", contract_address)
else:
    # Deploy contract
    StudentContract = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    )
    tx_hash = StudentContract.constructor().transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = tx_receipt.contractAddress
    abi = contract_interface["abi"]

    # Save deployment info
    with open(deploy_info_path, "w") as f:
        json.dump({"address": contract_address, "abi": abi}, f)

    contract = w3.eth.contract(address=contract_address, abi=abi)
    print("✅ Contract deployed and saved:", contract_address)

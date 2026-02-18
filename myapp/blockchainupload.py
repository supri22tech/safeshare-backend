from blockchain import contract, w3

def upload_code(data):
    try:
        tx_hash = contract.functions.addPostRecords(str(data[0]), data[1], data[2],data[3],
                                                      str(data[4])).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print("okkkkkkkkkkkkkkkkkkkkkkkk")
    except Exception as e:
        message = "Error: " + str(e)
        print(message)


data=input()
upload_code(data.split("**"))
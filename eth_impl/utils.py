from solcx import compile_source
from solcx import set_solc_version
import random


def ran_pick(seq: list, probabilities: list):
    x = random.uniform(0, 1)
    cum_prob = 0.0
    item = None
    for item, item_prob in zip(seq, probabilities):
        cum_prob += item_prob
        if x < cum_prob:
            break
    return item


def compile_source_file(file_path, solc_version='v0.5.17'):
    set_solc_version(solc_version)
    with open(file_path, 'r') as f:
        source = f.read()
    compiled_sol = compile_source(source, evm_version="byzantium")
    contract_id, contract_interface = compiled_sol.popitem()
    return contract_id, contract_interface


def deploy_bran_contract(
        w3,
        contract_interface,
        addr_user,
        addr_server,
        details,
        price,
        serv_time,
        deposit,
        sig_user,
        sig_server
):
    tx_hash = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
    ).constructor(addr_user, addr_server, details, price, serv_time, deposit, sig_user, sig_server).transact({
        "value": deposit
    })
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    address = tx_receipt['contractAddress']
    return address, tx_receipt


if __name__ == '__main__':
    value_list = [0, 1]
    prob = [0.2, 0.8]
    for i in range(20):
        print(type(ran_pick(value_list, prob)))

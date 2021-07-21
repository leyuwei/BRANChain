import sys
import csv
import time
from threading import Thread
import random
import gevent
# import pprint
import web3
import psrecord
from utils import compile_source_file, deploy_bran_contract
# from solcx import compile_source
# from web3.providers.eth_tester import EthereumTesterProvider
# from eth_tester import PyEVMBackend
# from solcx import set_solc_version_pragma, install_solc, get_solc_version, get_installed_solc_versions, set_solc_version


# str must be converted to type "address" (using web3.toChecksumAddress())
UE = "0x8eada06447c4618b3b6647643b90a3d601f396e0"
AP = "0x057d1155f7a1a18af0f8156d7ea20b2b6918cfd9"
MINER = "0x003962505e2d41108ae43eab47a709748ab86537"

# Contract args
DETAILS = "1"  # str
PRICE = 1  # uint
SERV_TIME = 10  # uint
DEPOSIT = 10  # uint
SIG_USER = "0x1"  # bytes
SIG_SERVER = "0x2"  # bytes

MAX_REQ_NUM = 5000
ACCOUNT_PW = "1234"
S = 2
RHO = 0.5
LAMBDA_C = 0.1
LAMBDA_A = RHO * S * LAMBDA_C


class UERequestThread(Thread):
    def __init__(self, ue_w3: web3.Web3, ap_address: str, req_size_l: list):
        """
        Deploy contract and pay deposit
        :param ue_w3:
        :param ap_address:
        :param req_size_l: list of the size of service request
        """
        super().__init__()
        self._ue_w3 = ue_w3
        self._ap_address = ap_address
        self._req_size_l = req_size_l

    def run(self) -> None:
        # Notice! start time
        req_start_time = time.time()
        self._ue_w3.eth.defaultAccount = self._ue_w3.eth.accounts[0]
        self._ue_w3.geth.personal.unlock_account(self._ue_w3.eth.accounts[0], ACCOUNT_PW, 100000)

        contract_source_path = "BranService.sol"
        bran_id, bran_interface = compile_source_file(contract_source_path)
        bytes_size = (sys.getsizeof(bran_interface['abi']) + sys.getsizeof(bran_interface['bin'])) / 1024
        item = [bytes_size, time.time()]
        self._req_size_l.append(item)
        bran_address, bran_receipt = deploy_bran_contract(
            self._ue_w3,
            bran_interface,
            self._ue_w3.toChecksumAddress(self._ue_w3.eth.accounts[0]),
            self._ue_w3.toChecksumAddress(self._ap_address),
            DETAILS.encode(encoding='utf-8'),
            PRICE,
            SERV_TIME,
            DEPOSIT,
            bytes(SIG_USER, encoding='utf8'),
            bytes(SIG_SERVER, encoding='utf8')
        )

        with open("req_start_time.csv", 'a') as f:
            writer = csv.writer(f)
            writer.writerow([bran_address, req_start_time])
        print(f'[CONTRACT DEPLOYMENT] Deployed {bran_id} to: {bran_address}\n')
        # print("Deploy BRAN tx receipt mined:")
        # pprint.pprint(dict(bran_receipt))
        # print(f'User balance is {ue_w3.eth.getBalance(ue_w3.eth.accounts[0])}')
        # print(f'Bran contract balance is {self._ue_w3.eth.getBalance(bran_address)}\n')

        # bran_service = self._ue_w3.eth.contract(address=bran_address, abi=bran_interface['abi'])
        # gas_estimate = bran_service.functions.payDeposit().estimateGas({'value': DEPOSIT})
        # if gas_estimate < 100000:
        #     print(f"[BRAN_ADDR: {bran_address}] Sending transaction to payDeposit\n")
        #
        #     pay_deposit_tx_hash = bran_service.functions.payDeposit().transact({
        #         'from': self._ue_w3.eth.accounts[0],
        #         'to': bran_address,
        #         'value': DEPOSIT
        #     })
        #     pay_deposit_receipt = self._ue_w3.eth.waitForTransactionReceipt(pay_deposit_tx_hash)
        #     # print(f'Bran contract balance is {ue_w3.eth.getBalance(bran_address)}\n')
        #     # print("payDeposit tx receipt mined:")
        #     # pprint.pprint(dict(pay_deposit_receipt))
        # else:
        #     print("Gas cost exceeds 100000")


def main():
    # ue1_w3 = Web3(EthereumTesterProvider(PyEVMBackend()))
    ue_w3 = web3.Web3(web3.Web3.HTTPProvider("http://localhost:8545"))
    # if ue_w3.isConnected() and ue_w3.clientVersion.startswith('Geth'):
    #     ue_enode = ue_w3.geth.admin.node_info()['enode']
    # TODO: networking
    # TODO: miner_w3.geth.miner.start(1); miner_w3.geth.miner.stop(); miner_w3.eth.mining; miner_w3.eth.hashrate
    req_size_l = []
    ue_threads = []
    for _ in range(MAX_REQ_NUM):
        ue_t = UERequestThread(ue_w3, AP, req_size_l)
        ue_threads.append(ue_t)
        ue_t.start()
        # print(f'[REQUEST SUBMITTED] Progress: {i + 1} / {MAX_REQ_NUM}')
        secs = random.expovariate(LAMBDA_A)
        gevent.sleep(secs)
    for ue_t in ue_threads:
        ue_t.join()

    with open("size_req.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerows(req_size_l)


if __name__ == '__main__':
    main()
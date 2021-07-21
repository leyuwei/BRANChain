# import sys
import time
import csv
# import pprint
import web3
import random
from threading import Thread, Lock
from utils import compile_source_file, ran_pick
# from solcx import compile_source
# from web3.providers.eth_tester import EthereumTesterProvider
# from eth_tester import PyEVMBackend
# from solcx import set_solc_version_pragma, install_solc, get_solc_version, get_installed_solc_versions, set_solc_version
UE = "0x8eada06447c4618b3b6647643b90a3d601f396e0"
AP = "0x057d1155f7a1a18af0f8156d7ea20b2b6918cfd9"
MINER = "0x003962505e2d41108ae43eab47a709748ab86537"
ACCOUNT_PW = "1234"
CONFIRMATION_NUM = 3
LAMBDA_C = 0.1


class Counter(object):
    """
        A thread-safe counter used to record the number of services
    """
    def __init__(self):
        self._count = 0
        self._lock = Lock()

    def increase(self):
        self._lock.acquire()
        try:
            self._count = self._count + 1
        finally:
            self._lock.release()

    @property
    def count(self):
        return self._count


class ContractInfo(object):
    """
        Record contract info including address, block number, and timestamp
    """
    def __init__(self, address: str, block_number):
        self._address = address
        self._block_number = block_number
        self._timestamp = time.time()

    def __str__(self):
        return f'address: {self.address}, block_number: {self.block_number}, timestamp: {self.timestamp}'

    def __repr__(self):
        return f'address: {self.address}, block_number: {self.block_number}, timestamp: {self.timestamp}'

    @property
    def address(self):
        return self._address

    @property
    def block_number(self):
        return self._block_number

    @property
    def timestamp(self):
        return self._timestamp


class ContractPool(object):
    """
        The essence of ContractPool is FIFO queue
    """
    def __init__(self):
        self._contract_info_list = []
        self._lock = Lock()

    # Head Insert
    def add_contract_info(self, contract_info: ContractInfo):
        self._lock.acquire()
        try:
            self.contract_info_list.insert(0, contract_info)
        finally:
            self._lock.release()

    def get_info_by_index(self, index) -> ContractInfo:
        self._lock.acquire()
        try:
            info = self._contract_info_list[index]
        finally:
            self._lock.release()
        return info

    def pop_contract_info(self, contract_index) -> ContractInfo:
        self._lock.acquire()
        try:
            info = self.contract_info_list.pop(contract_index)
        finally:
            self._lock.release()
        return info

    @property
    def contract_info_list(self):
        return self._contract_info_list


class APServiceThread(Thread):
    """
    APServiceThread calls the web3 API. triggers the bran service in a contract with a specified address,
    and ends the service in serv_time seconds after starting the service.
    """
    def __init__(self, ap_w3: web3.Web3, contract_address: str, serv_time: float):
        super().__init__()
        self._ap_w3 = ap_w3
        self._contract_address = contract_address
        self._serv_time = serv_time
        self._served = False

    def run(self) -> None:
        self._ap_w3.eth.defaultAccount = self._ap_w3.eth.accounts[0]
        self._ap_w3.geth.personal.unlock_account(self._ap_w3.eth.accounts[0], ACCOUNT_PW, 100000)
        contract_source_path = "BranService.sol"
        bran_id, bran_interface = compile_source_file(contract_source_path)

        # find the bran contract in blockchain
        bran_service = self._ap_w3.eth.contract(address=self._ap_w3.toChecksumAddress(self._contract_address), abi=bran_interface['abi'])
        serv_start_time = None
        serv_end_time = None

        # start service
        gas_estimate = bran_service.functions.start_service().estimateGas()
        if gas_estimate < 100000:
            print(f"[AP_ADDR: {self._ap_w3.eth.accounts[0]} | BRAN_ADDR: {self._ap_w3.toChecksumAddress(self._contract_address)}] Sending transaction to start service\n")

            start_service_tx_hash = bran_service.functions.start_service().transact({
                'from': self._ap_w3.eth.accounts[0],
                'to': self._ap_w3.toChecksumAddress(self._contract_address)
            })
            start_service_receipt = self._ap_w3.eth.waitForTransactionReceipt(start_service_tx_hash)
            # record the time when service start
            serv_start_time = time.time()
            print(
                f'[Start_service | BRAN_ADDR: {self._ap_w3.toChecksumAddress(self._contract_address)}] '
                f'Bran contract balance is '
                f'{self._ap_w3.eth.getBalance(self._ap_w3.toChecksumAddress(self._contract_address))}\n')
            # print("start_service tx receipt mined:")
            # pprint.pprint(dict(start_service_receipt))
        else:
            print("Gas cost exceeds 100000")

        time.sleep(self._serv_time)

        # end service
        gas_estimate = bran_service.functions.end_service().estimateGas()
        if gas_estimate < 100000:
            print(
                f"[AP_ADDR: {self._ap_w3.eth.accounts[0]} | BRAN_ADDR: {self._ap_w3.toChecksumAddress(self._contract_address)}] Sending transaction to end service\n")
            end_service_tx_hash = bran_service.functions.end_service().transact({
                'from': self._ap_w3.eth.accounts[0],
                'to': self._ap_w3.toChecksumAddress(self._contract_address)
            })
            end_service_receipt = self._ap_w3.eth.waitForTransactionReceipt(end_service_tx_hash)
            serv_end_time = time.time()
            print(
                f'[End_service| BRAN_ADDR: {self._ap_w3.toChecksumAddress(self._contract_address)}] '
                f'Bran contract balance is '
                f'{self._ap_w3.eth.getBalance(self._ap_w3.toChecksumAddress(self._contract_address))}\n')
            # print("end_service tx receipt mined:")
            # pprint.pprint(dict(end_service_receipt))
        else:
            print("Gas cost exceeds 100000")
        # Record the start and end time
        with open("serv_start_end_time.csv", 'a') as f:
            writer = csv.writer(f)
            writer.writerow([self._ap_w3.toChecksumAddress(self._contract_address), serv_start_time, serv_end_time])
        self._served = True

    @property
    def served(self):
        return self._served


class ServiceWindows(object):
    """
        The essence of ServiceWindows is a List which adds new APServiceThread and deletes served APServiceThread.
    """

    def __init__(self, max_win_num=2):
        self._windows = []
        self._lock = Lock()
        self._max_win_num = max_win_num

    def add_service(self, ap_service_thread: APServiceThread):
        if self.is_full():
            print("\033[0;31;40mError: all service windows are full!\033[0m")
            return
        self._lock.acquire()
        try:
            self._windows.append(ap_service_thread)
        finally:
            self._lock.release()

    def del_served_service(self):
        self._lock.acquire()
        try:
            for i in range(len(self._windows) - 1, -1, -1):
                if self._windows[i].served:
                    _ = self._windows.pop(i)
        finally:
            self._lock.release()

    def is_empty(self):
        return self._windows == []

    def is_full(self):
        return len(self._windows) == self.max_win_num

    def size(self):
        return len(self._windows)

    @property
    def windows(self):
        return self._windows

    @property
    def max_win_num(self):
        return self._max_win_num


class APGainServiceInfoThread(Thread):
    """
        Gain the tx whose "to" field is ap_address, and add the contract_info in tx to ContractPool
    """
    def __init__(self, ap_w3: web3.Web3, ap_address: str, contract_pool: ContractPool, service_counter: Counter):
        super().__init__()
        self._ap_w3 = ap_w3
        self._ap_address = ap_address
        self._contract_pool = contract_pool
        self._service_counter = service_counter

    def run(self) -> None:
        print('Listening...')
        # Record scanned_block_index if this thread has scanned the blockchain at this block height.
        scanned_block_index = -1
        while True:
            # scan blockchain and find the latest block
            # actually, current_block_index == 'latest'
            current_block_index = self._ap_w3.eth.blockNumber
            if scanned_block_index == current_block_index:
                continue

            block = self._ap_w3.eth.getBlock(current_block_index)
            if len(block['transactions']) == 0:
                scanned_block_index = current_block_index
                continue
            else:
                for tx_hash in block['transactions']:
                    tx_receipt = self._ap_w3.eth.getTransactionReceipt(tx_hash)
                    contract_address = tx_receipt['contractAddress']
                    if contract_address is None:
                        continue
                    elif self._ap_address[2:] in self._ap_w3.eth.getTransaction(tx_hash)['input']:
                        # TODO: Record the requests count hosts receive
                        self._service_counter.increase()
                        rcv_serv_timestamp = time.time()
                        print(f'[FIND SERVICE | NO.{self._service_counter.count}]')
                        with open("rcv_serv_num.csv", 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow([self._service_counter.count, rcv_serv_timestamp])
                        # TODO: construct an instance with 'contractAddress' and put it into a list
                        contract_info = ContractInfo(contract_address, current_block_index)
                        self._contract_pool.add_contract_info(contract_info)
            scanned_block_index = current_block_index


class APSelectServiceThread(Thread):
    def __init__(self, ap_w3: web3.Web3, contract_pool: ContractPool, service_windows: ServiceWindows, net_serv_count: Counter):
        super().__init__()
        self._ap_w3 = ap_w3
        self._contract_pool = contract_pool
        self._service_windows = service_windows
        self._net_serv_count = net_serv_count

    def run(self) -> None:
        while True:
            self._service_windows.del_served_service()
            if self._service_windows.is_full():
                continue
            current_block_index = self._ap_w3.eth.blockNumber

            # Reverse traversal
            for idx in range(len(self._contract_pool.contract_info_list) - 1, -1, -1):
                if self._service_windows.is_full():
                    break
                elif self._contract_pool.get_info_by_index(idx).block_number + CONFIRMATION_NUM <= current_block_index:
                    contract_info = self._contract_pool.pop_contract_info(idx)
                    flag = ran_pick([0, 1], [0.2, 0.8])
                    if flag == 1:
                        self._net_serv_count.increase()
                        timestamp = time.time()
                        print(f'[ACTUALLY SERVE | NO.{self._net_serv_count.count}]')
                        # TODO: Record the requests count hosts actually serve
                        with open("actually_serv_num.csv", 'a') as f:
                            writer = csv.writer(f)
                            writer.writerow([self._net_serv_count.count, timestamp])
                        # TODO: start bran service and end bran service
                        serv_time = random.expovariate(LAMBDA_C)
                        service_thread = APServiceThread(self._ap_w3, contract_info.address, serv_time)
                        self._service_windows.add_service(service_thread)
                        service_thread.start()


def main():
    ap_w3 = web3.Web3(web3.Web3.HTTPProvider("http://localhost:8546"))
    cp = ContractPool()
    sw = ServiceWindows()
    serv_counter = Counter()
    net_serv_counter = Counter()
    ap_gain_service_thread = APGainServiceInfoThread(ap_w3, AP, cp, serv_counter)
    ap_select_service_thread = APSelectServiceThread(ap_w3, cp, sw, net_serv_counter)
    ap_gain_service_thread.start()
    ap_select_service_thread.start()
    # ap_gain_service_thread.join()
    # ap_select_service_thread.join()


if __name__ == '__main__':
    main()

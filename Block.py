from Hash import *
import time
import threading
from typing import Dict, List, Tuple

import json

class Block (object):
    def __init__(self, previous_hash, transactions):
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.data = str(previous_hash) + str(transactions)
        self.hash = str(self.calculate_hash())

    def calculate_hash(self):
        return str(Hash(self.data))

    def __str__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

class BlockChain (object):
    def __init__(self):
        self.blocks = []
        self.miners = []
        self.pending_transactions = []
        threading.Thread(target=self.start_timer).start()
        self.account: Dict[str, Tuple[int, int]] = {}


    def add_block(self, data):
        # Check if this is the first block being added to the chain
        if len(self.blocks) == 0:
            previous_block_hash = None
        else:
            previous_block_hash = self.blocks[-1].hash

        # Create a new block and add it to the chain
        new_block = Block(previous_block_hash, data)
        self.blocks.append(new_block)

    def is_valid(self):
        # Iterate over the blocks in the chain and check if they are valid
        for i in range(1, len(self.blocks)):
            current_block = self.blocks[i]
            previous_block = self.blocks[i - 1]

            # Check if the current block's data is valid
            # (You can use your signature module to do this)
            if not self.is_data_valid(current_block.data):
                return False

            # Check if the current block's hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False

            # Check if the current block points to the correct previous block
            if current_block.previous_block_hash != previous_block.hash:
                return False

        # If all checks pass, the chain is valid
        return True

    def is_data_valid(self, data):
        # Use your signature module to check if the data is valid
        pass

    def add_miner(self, miner):
        self.miners.append(miner)

    def mine(self):
        miner = random.choice(self.miners)
        miner.mine(self)
        self.pending_transactions = []
        return self.blocks[-1]

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)
        if len(self.pending_transactions) > 10:
            self.mine()

    def start_timer(self):
        while True:
            time.sleep(10)
            if len(self.pending_transactions) > 0:
                # mine the transactions
                self.mine()

    def __str__(self):
        return str(self.blocks)

    def print_chain(self):
        s = ""
        for block in self.blocks:
            s+=str(block)
            s+=":   "
            s+=str(block.transactions)
            s+='\n'
        return s



class Miner (object):
    def __init__(self, name):
        self.name = name

    def mine(self, blockchain):
        # Mine a block and add it to the chain
        blockchain.add_block("Block mined by " + self.name + "\nTransactions: " + str(blockchain.pending_transactions))
        print(blockchain.print_chain())



def handle_transaction(json_data):
    data = json.loads(json.dumps(json_data))
    from_address = data['from']
    to_address = data['to']
    amount = data['amount']
    transaction_str = f"{from_address} sent {amount} to {to_address}"
    return transaction_str


def add_transaction_to_history(transaction):
    with open('transaction_history.txt', 'a') as f:
        f.write(str(transaction) + '\n')



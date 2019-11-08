from transaction import *
# from wallet import *
BLOCK_INCENTIVE = 2 # The number of coins miners get for mining a block
DIFFICULTY = 2


def mint(message, difficulty=1):
    #TODO CHANGE TO MINING BASED ON STAKE 
    """
    Given an input string, will return a nonce such that
    hash(string + nonce) starts with `difficulty` ones
    
    Returns: (nonce, niters)
        nonce: The found nonce
        niters: The number of iterations required to find the nonce
    """
    # assert difficulty >= 1, "Difficulty of 0 is not possible"
    # i = 0
    # prefix = '1' * difficulty
    # while True:
    #     nonce = str(i)
    #     digest = Transaction.sha256_hash(message + nonce)
    #     if digest.startswith(prefix):
    #         return nonce, i
    #     i += 1

def compute_total_fee(transactions):
    """Return the total fee for the set of transactions"""
    return sum(t.fee for t in transactions)


class Block(object):
    def __init__(self, transactions, ancestor, miner_address, timestamp, skip_verif=False):
        """
        Args:
            transactions: The list of transactions to include in the block
            ancestor: The previous block
            miner_address: The address of the miner's wallet. This is where the block
                           incentive and the transactions fees will be deposited
        """
        reward = compute_total_fee(transactions) + BLOCK_INCENTIVE
        coinbase_transaction = CoinbaseTransaction()
        # https://naivecoinstake.learn.uno/03-Transactions/
        self.transactions = [coinbase_transaction, StakingTransaction(miner_address, amount=reward)] + transactions
        self.ancestor = ancestor
        
        if not skip_verif:
            assert all(map(verify_transaction, transactions))
        
        json_block = json.dumps(self.to_dict(include_hash=False))
        self.nonce, _ = mine(json_block, DIFFICULTY)
        self.hash = hash(json_block + self.nonce)
        
    def fee(self):
        """Return transaction fee for this block"""
        return compute_total_fee(self.transactions)
    
    def to_dict(self, include_hash=True):
        d = {
            "transactions": list(map(Transaction.to_dict, self.transactions)),
            "previous_block": self.ancestor.hash,
        }
        if include_hash:
            d["nonce"] = self.nonce
            d["hash"] = self.hash
        return d
    
    
class GenesisBlock(Block):
    """
    The genesis block is the first block in the chain.
    It is the only block with no ancestor
    """
    def __init__(self, miner_address):
        super(GenesisBlock, self).__init__(transactions=[], ancestor=None, miner_address=miner_address)

    def to_dict(self, include_hash=True):
        d = {
            "transactions": [],
            "genesis_block": True,
        }
        if include_hash:
            d["nonce"] = self.nonce
            d["hash"] = self.hash
        return d

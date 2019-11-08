from transaction import *
# from wallet import *
BLOCK_INCENTIVE = 2 # The number of coins miners get for mining a block
DIFFICULTY = 0x0000000100000000000000000000000000000000000000000000000000000000


def mint(message, stake_value, difficulty=DIFFICULTY):
    #TODO CHANGE TO MINTING BASED ON STAKE using Kernel Hash 
    """
    Given an input string, will return a nonce such that
    hash(string + nonce) starts with `difficulty` zeros
    
    Returns: (nonce, niters)
        nonce: The found nonce
        niters: The number of iterations required to find the nonce
    """
    assert difficulty >= 1, "Difficulty of 0 is not possible"
    i = 0
    while True:
        nonce = str(i)
        digest = Transaction.sha256_hash(message + nonce)
        # if digest.startswith(prefix):
        if digest < difficulty * stake_value:
            return nonce, i
        i += 1


def compute_total_fee(transactions):
    """Return the total fee for the set of transactions"""
    return sum(t.fee for t in transactions)

class Minter:
    def __init__(self, name, wallet_address, stake_value):
        self.address = wallet_address
        self.stake_value = stake_value
        self.name = name

class Block(object):
    def __init__(self, transactions, ancestor, minter, timestamp, skip_verif=False):
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
        self.transactions = [coinbase_transaction, StakingTransaction(minter.address, amount=reward)] + transactions
        self.ancestor = ancestor
        self.minter = minter
        if not skip_verif:
            assert all(map(verify_transaction, transactions))
        
        json_block = json.dumps(self.to_dict(include_hash=False))
        self.nonce, _ = mint(json_block, minter.stake_value, DIFFICULTY)
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
    def __init__(self, minter):
        super(GenesisBlock, self).__init__(transactions=[], ancestor=None, minter = minter)

    def to_dict(self, include_hash=True):
        d = {
            "transactions": [],
            "genesis_block": True,
        }
        if include_hash:
            d["nonce"] = self.nonce
            d["hash"] = self.hash
        return d

def verify_block(block, genesis_block, used_outputs=None, ):
    """
    Verifies that a block is valid :
    - Verifies the hash is less than weighter difficulty
    - Verifies that the same transaction output isn't used twice
    - Verifies all transactions are valid
    - Verifies the first transaction in the block is a coinbase transaction with 0 fee and the second is a Staking transaction 
    with BLOCK_INCENTIVE + total_fee
    
    Args:
        block: The block to validate
        genesis_block: The genesis block (this needs to be shared by everybody. E.g. hardcoded somewhere)
        used_outputs: list of outputs used in transactions for all blocks above this one
    """
    if used_outputs is None:
        used_outputs = set()
    
    # Verify hash
    pos_difficulty = block.minter.stake * DIFFICULTY
    if not block.hash < pos_difficulty:
        logging.error("Block hash (%s) satisfy weighted difficulty" % (block.hash))
        return False
    if not all(map(verify_transaction, block.transactions)):
        return False
    
    # Verify that transactions in this block don't use already spent outputs
    #
    # Note that we could move this in verify_transaction, but this would require some passing the used_outputs
    # around more. So we do it here for simplicity
    for transaction in block.transactions:
        for i in transaction.inputs:
            if i.parent_output in used_outputs:
                logging.error("Transaction uses an already spent output : %s" % json.dumps(i.parent_output.to_dict()))
                return False
            used_outputs.add(i.parent_output)
    
    # Verify ancestors up to the genesis block
    if not (block.hash == genesis_block.hash):
        if not verify_block(block.ancestor, genesis_block, used_outputs):
            logging.error("Failed to validate ancestor block")
            return False
    
    # Verify the second transaction is the miner's reward
    tx0 = block.transactions[0]
    tx1 = block.transactions[1]

    if not isinstance(tx0, CoinbaseTransaction):
        logging.error("Transaction 0 is not a CoinbaseTransaction")
        return False
    if not len(tx0.outputs) == 0:
        logging.error("Transactions 0 doesn't have exactly 0 output")
        return False
    if not isinstance(tx1, StakingTransaction):
        logging.error("Transaction 1 is not a StakingTransaction")
        return False    
    reward = compute_total_fee(block.transactions[1:]) + BLOCK_INCENTIVE
    if not tx1.outputs[0].amount == reward:
        logging.error("Invalid amount in transaction 0 : %d, expected %d" % (tx0.outputs[0].amount, reward))
        return False
    
    # Only the first transaction shall be a coinbase transaction
    for i, tx in enumerate(block.transactions):
        if i == 0:
            if not isinstance(tx, CoinbaseTransaction):
                logging.error("Non-genesis transaction at index 0")
                return False  
        elif isinstance(tx, CoinbaseTransaction):
            logging.error("GenesisTransaction (hash=%s) at index %d != 0", tx.hash(), i)
            return False
    return True
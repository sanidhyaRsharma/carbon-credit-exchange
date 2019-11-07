import hashlib
import random
import string
import json
import binascii
import numpy as np
import pandas as pd
import logging

class TransactionInput(object):
    """
    An input for a transaction. This points to an output of another transaction
    """
    def __init__(self, transaction, output_index):
        self.transaction = transaction
        self.output_index = output_index
        assert 0 <= self.output_index < len(transaction.outputs)
        
    def to_dict(self):
        d = {
            'transaction': self.transaction.hash(),
            'output_index': self.output_index
        }
        return d
    
    @property
    def parent_output(self):
        return self.transaction.outputs[self.output_index]
    

class TransactionOutput(object):
    """
    An output for a transaction. This specifies an amount and a recipient (wallet)
    """
    def __init__(self, recipient_address, amount):
        self.recipient = recipient_address
        self.amount = amount
        
    def to_dict(self):
        d = {
            'recipient_address': self.recipient,
            'amount': self.amount
        }
        return d

        
def compute_fee(inputs, outputs):
    """
    Compute the transaction fee by computing the difference between total input and total output
    """
    total_in = sum(i.transaction.outputs[i.output_index].amount for i in inputs)
    total_out = sum(o.amount for o in outputs)
    assert total_out <= total_in, "Invalid transaction with out(%f) > in(%f)" % (total_out, total_in)
    return total_in - total_out

    
class Transaction(object):
    def __init__(self, wallet, inputs, outputs):
        """
        Create a transaction spending money from the provided wallet
        """
        self.inputs = inputs
        self.outputs = outputs
        self.fee = compute_fee(inputs, outputs)
        self.signature = wallet.sign(json.dumps(self.to_dict(include_signature=False)))
        
    def to_dict(self, include_signature=True):
        d = {
            "inputs": list(map(TransactionInput.to_dict, self.inputs)),
            "outputs": list(map(TransactionOutput.to_dict, self.outputs)),
            "fee": self.fee
        }
        if include_signature:
            d["signature"] = self.signature
        return d
    
    @staticmethod
    def sha256_hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def hash(self):
        return self.sha256_hash(json.dumps(self.to_dict()))

class CoinbaseTransaction:
    """
    This is the first transaction: Empty and 0 reward
    """

class StakeTransaction:
    """
    This is the second transaction in PoS having 1 vin and atleast 2 vouts with first vout being empty
    """


def compute_balance(wallet_address, transactions):
    """
    Given an address and a list of transactions, computes the wallet balance of the address
    """
    balance = 0
    for t in transactions:
        # Subtract all the money that the address sent out
        for txin in t.inputs:
            if txin.parent_output.recipient == wallet_address:
                balance -= txin.parent_output.amount
        # Add all the money received by the address
        for txout in t.outputs:
            if txout.recipient == wallet_address:
                balance += txout.amount
    return balance

def verify_transaction(transaction):
    """
    Verify that the transaction is valid.
    We need to verify two things :
    - That all of the inputs of the transaction belong to the same wallet
    - That the transaction is signed by the owner of said wallet
    """
    tx_message = json.dumps(transaction.to_dict(include_signature=False))
    if isinstance(transaction, CoinbaseTransaction):
        # TODO: We should probably be more careful about validating genesis transactions
        return True
    
    # Verify input transactions
    for tx in transaction.inputs:
        if not verify_transaction(tx.transaction):
            logging.error("Invalid parent transaction")
            return False
    
    # Verify a single wallet owns all the inputs
    first_input_address = transaction.inputs[0].parent_output.recipient
    for txin in transaction.inputs[1:]:
        if txin.parent_output.recipient != first_input_address:
            logging.error(
                "Transaction inputs belong to multiple wallets (%s and %s)" %
                (txin.parent_output.recipient, first_input_address)
            )
            return False
    
    if not verify_signature(first_input_address, tx_message, transaction.signature):
        logging.error("Invalid transaction signature, trying to spend someone else's money ?")
        return False
    
    # Call compute_fee here to trigger an assert if output sum is great than input sum. Without this,
    # a miner could put such an invalid transaction.
    compute_fee(transaction.inputs, transaction.outputs)
    
    return True
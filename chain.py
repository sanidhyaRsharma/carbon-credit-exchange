from block import *
from uuid import uuid4
from urllib.parse import urlparse
import requests
from flask import jsonify, request, Flask
class Blockchain:
    def __init__(self):
        self.transaction_pool = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace('-','')
        self.last_block = GenesisBlock(Minter('God','00','1000'))
        self.genesis_block = self.last_block
        self.length = self.chain_length(self.last_block)

    def register_node(self, node_url):
        """
        Add a new node to the list of nodes
        """
        #Checking node_url has valid format
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')
    
    def chain_length(self, block):
        if block.ancestor is None:
            return 1
        return 1 + self.chain_length(block.ancestor) 

    def broadcast_transaction(self, transaction):
        neighbours = self.nodes
        for node in neighbours:
            #TODO send a request to all the nodes to add a transaction to their pool
            url = f'http://{node}/add-transaction-to-pool'
            res = requests.post(url, json = transaction)
            return res

    def broadcast_block(self, block):
        neighbours = self.nodes
        for node in neighbours:
            #TODO send a request to all the nodes to verify and add a block to their chain
            url = f'http://{node}/verify-and-add-block'
            res = requests.post(url, json = block)
            return res
    
    def verify_chain(self, block):
        if not (block.hash == self.genesis_block.hash):
            if not self.verify_chain(block.ancestor):
                logging.error("Failed to validate ancestor block")
                return False
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        longest_chain_length = self.chain_length(self.last_block)
        for node in neighbours:
            #TODO compare lengths and replace current with longer chain(if found)
            url = f'http://{node}/chain'
            res = requests.get(url)

            if res.status_code == 200:
                length = res.json()['length']
                chain = res.json()['chain']

                if length > longest_chain_length and self.verify_chain(chain.last_block):
                    self.last_block = chain.last_block
                    self.length = length
                    # How to share and sync transaction_pool? How to delete used transactions from pool?
            
    
app = Flask(__name__)
blockchain = Blockchain()

@app.route('/add-transaction-to-pool', methods=['POST'])
def add_transaction_to_pool(data):
    #TODO: Add a transaction received as POST to blockchain.transaction_pool
    pass

@app.route('/verify-and-add-block', methods=['POST'])
def verify_and_add_block():
    #TODO: Add a block received as POST to blockchain.last_block
    pass

@app.route('/chain')
def chain():
    #TODO: Send blockchain.last_block's deep copy and the chain length as a response
    pass
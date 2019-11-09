from block import *
from uuid import uuid4
from urllib.parse import urlparse
from transaction import *
from block import *

class Blockchain:
    def __init__(self):
        self.transaction_pool = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace('-','')
        self.last_block = GenesisBlock(Minter('God','00','1000'))
        self.genesis_block=self.last_block

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
            response=requests.post(f'http:/{node}/get_transaction',json={"transaction":transaction})
            #pass
    def get_transaction():
        json=request.get_json()
        transaction=json.get("transaction")
        if verify_transaction(transaction):
            self.transaction_pool.append(transaction)
            
    def broadcast_block(self, block):
        neighbours = self.nodes
        for node in neighbours:
            response=requests.post(f'http:/{node}/get_block',json={"block":block})
            #TODO send a request to all the nodes to verify and add a block to their chain
            #pass
            
    def get_block():
        json=request.get_json()
        block=json.get("block")
        if verify_block(block,self.genesis_block):
            last_block=self.last_block
            block.ancestor=last_block
            #self.chain.append(block)
    def get_chain_length():
        length=self.chain_length
        response={"length":length}
        return jsonify(response),200
    def get_last_block():
        last_block=self.last_block
        response={"last_block":last_block}
        return jsonify(response),200
    
    def resolve_conflicts(self):
        neighbours = self.nodes
        max_length=self.chain_length
        longest_chain_last_block=None
        for node in neighbours:
            response=requests.get(f'http:/{node}/get_chain_length')
            length=response.json()['length']
            if length>max_length:
                node_response=response.get(f'http:/{node}/get_last_block')
                longest_node_last_block=node_response.json()['last_block']
        if longest_node_last_block is not None:
            self.last_block=longest_node_last_block
            #TODO compare lengths and replace current with longer chain(if found)
            #pass
    
    
from block import *
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.transaction_pool = []
        self.nodes = set()
        self.node_id = str(uuid4()).replace('-','')
        self.last_block = GenesisBlock(Minter('God','00','1000'))

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
            pass

    # def resolve_conflicts(self,)
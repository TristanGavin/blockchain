import hashlib
import json

from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask


class Blockchain(object):
    def __init__(self):   #object constructor 
        #initialize chain and transaction
        self.chain = []   
        self.current_transactions = []

        #create genesis block
        self.new_block(previous_hash=1, proof=100)
    
    def new_block(self, previous_hash, proof):
        #defines new block and adds it to chain
        """
        create a new block in the blockchain
        param previous_hash (int) OPTIONAL - previous blocks proof of work
        param proof (int) - this blocks proof of work created with algorithm
        return block (dict) - the new block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) # what is going on with this line??
        }

        # reset current transactions after block has been created
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        #defines new transaction and adds it to transaction
        """
        create a new transaction to go into the next mined block
        :param sender (str)
        :param recipient (str)
        :param amount (int)
        :param index of block (int)
        """
        #append transaction to end of current transaction list
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index']+1 #return index of block transaction is to be added to.
        
    def proof_of_work(self, last_proof):
        """
        simple proof of work algorithm
        -find a number p for which hash(pp') has 4 leading zeroes, where p is the previous p'
        -p is the previous proof and p' is the new proof
        :param last_proof (int)
        :return proof (int)
        """
        #initialize proof.
        proof = 0
        # loop incrementing p' looking for a p' that sets the first 4 digits of hash to 0
        while self.valid_proof(last_proof, proof) is False:
            proof +=1 
        
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        checks the currrent proof to make see if it produces 4 leading 0s 
        the more leading zeroes required the more computationally expensive this step is.
        :last_proof (int) - last proof
        :proof (int) - current proof
        """
        guess = f'{last_proof}{proof}'.encode() # encode last_prrof and prrof as a string
        guess_hash = hashlib.sha256(guess).hexdigest()
        #if the first 4 digists of guess_hash are 0 return true.
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        #hash a block using sha-256
        """
        param block (dict) - block to be hashed
        return (str)
        """
        # encode the block with json.dump
        block_string = json.dumps(block, sort_keys=True).encode()
        # return a sha256 hashcode of the block string created above.
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):

        #returns last block in chain
        return self.chain[-1]

    ### CODE FOR FLASK SERVER ###
    #we want a way to mine new blocks, post new transactions and get the full blockchain.

    # Instantiate the node 
    app = Flask(__name__)

    # Generate a globally unique name for this node
    node_identifier = str(uuid4()).replace('-', '')

    # Instantiate the blockchain
    blockchain = Blockchain()
    
    #define the HTTP operations that can be performed.
    @app.route('/mine', methods=['GET'])
    def mine():
        return "we will mine a new block"

    @app.route('/transactions/new', methods=['POST'])
    def new_transaction():
        return "add a new transaction"

    @app.route('/chain', methods=['GET'])
    def chain():
        return "return the entire blockchain"
    



        
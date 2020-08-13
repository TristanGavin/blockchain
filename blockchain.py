# Blockchain Code
# by Tistan Gavin
# Borrowed heavily from: https://hackernoon.com/learn-blockchains-by-building-one-117428612f46 
# Learn Blockchains by Building one
# 
# Thoughts:
# Have a much better comprehension of how blockchains and crypto currency works. Each block is linked together
# by a unique discovered hash code that turns the first x amount of numbers into zeros. Changing one message would
# break the code all the way down. It is computationally expensive for codes to be found and miners are rewarded
# with currency for finding them and adding a block to the chain. 
#
# Complications:
# Ran into an issue with my server side new_transaction function. Kept getting a HTTP 500 error.
#
# TODO:
# Fix new_transaction.
# Finish decentralizing the chain so that everyone has a copy
# going to work on a different project for now.


import hashlib
import json

from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request


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

# define the HTTP operations that can be performed.
# route() tells flask what url triggers our function
@app.route('/mine', methods=['GET'])
def mine():
    # mine method must calculate proof of work, reward miner with 1 coin, add the new block to the chain.
    # run proof of work algorithm.
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # reward miner with block
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # add new block to the chain.
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(previous_hash, proof)

    # http response message.
    response = {
        'message': "New block forged", 
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200

# POST request since we are sending data
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201
    


@app.route('/chain', methods=['GET'])
def chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200

# run server of port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




    
    



        
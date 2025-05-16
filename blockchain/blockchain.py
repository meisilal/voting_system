import hashlib
import time

class Block:
    def __init__(self, index, data, previous_hash):
        self.timestamp = time.time()
        self.index = index
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        record = f'{self.index}{self.timestamp}{self.data}{self.previous_hash}'
        return hashlib.sha256(record.encode()).hexdigest()
    
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")
    
    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), data, previous_block.hash)
        self.chain.append(new_block)
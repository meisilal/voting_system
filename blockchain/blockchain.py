import hashlib
import time

blockchain = []

def create_block(data):
    previous_hash = blockchain[-1]['hash'] if blockchain else '0'
    block = {
        'index': len(blockchain) + 1,
        'timestamp': time.time(),
        'data': data,
        'previous_hash': previous_hash,
    }
    block_string = f"{block['index']}{block['timestamp']}{block['data']}{previous_hash}"
    block['hash'] = hashlib.sha256(block_string.encode()).hexdigest()
    blockchain.append(block)
    return block

def add_vote_to_chain(voter_uid, vote):
    # data includes voter_uid for traceability
    data = {'voter_uid': voter_uid, 'vote': vote}
    create_block(data)
    return True

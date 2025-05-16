from blockchain.blockchain import vote_chain

def verify_chain():
    for i in range(1, len(vote_chain.chain)):
        current = vote_chain.chain[i]
        previous = vote_chain.chain[i - 1]
        if current.previous_hash != previous.hash:
            return False
    return True
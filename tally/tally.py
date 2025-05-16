from blockchain.blockchain import blockchain

def tally_votes():
    results = {}
    for block in blockchain:
        vote = block['data'].get('vote')
        if vote:
            results[vote] = results.get(vote, 0) + 1
    return results
from collections import defaultdict
from blockchain.blockchain import vote_chain

def tally_votes():
    results = defaultdict(int)
    for block in vote_chain.chain[1:]: #Skips genesis block
        candidate = block.data["candidate"]
        results[candidate] += 1
    return dict(results)